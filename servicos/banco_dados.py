"""
Serviço de Gerenciamento do Banco de Dados PostgreSQL.

Implementa todas as operações de banco de dados para o agente de otimização,
incluindo armazenamento de análises, consultas de histórico e estatísticas.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from configuracao.configuracao_bd import ConfiguracaoBancoDados
from modelos.schemas import HistoricoAnalise, Sugestao

logger = logging.getLogger(__name__)

class GerenciadorBancoDados:
    """
    Gerenciador principal do banco de dados PostgreSQL.
    
    Responsável por todas as operações de persistência de dados,
    incluindo análises, histórico e estatísticas.
    """
    
    def __init__(self):
        self.config = ConfiguracaoBancoDados()
        self.pool_conexoes = None
        self.engine = None
        
    async def inicializar_banco(self):
        """Inicializa a conexão com o banco de dados e cria as tabelas necessárias."""
        try:
            logger.info("Inicializando conexão com PostgreSQL...")
            
            # Cria o pool de conexões
            self.pool_conexoes = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.porta,
                user=self.config.usuario,
                password=self.config.senha,
                database=self.config.nome_banco,
                min_size=self.config.min_conexoes,
                max_size=self.config.max_conexoes,
                command_timeout=60
            )
            
            # Cria as tabelas se não existirem
            await self._criar_tabelas()
            
            logger.info("Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    async def _criar_tabelas(self):
        """Cria as tabelas necessárias no banco de dados."""
        sql_criar_tabelas = """
        -- Tabela principal para histórico de análises
        CREATE TABLE IF NOT EXISTS analysis_history (
            id SERIAL PRIMARY KEY,
            code_snippet TEXT NOT NULL,
            suggestions JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            pontuacao_qualidade DECIMAL(5,2),
            nome_arquivo VARCHAR(255),
            tempo_analise DECIMAL(8,4),
            nivel_detalhamento VARCHAR(20),
            numero_sugestoes INTEGER,
            tipos_sugestoes JSONB
        );
        
        -- Índices para melhor performance
        CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
        ON analysis_history(created_at);
        
        CREATE INDEX IF NOT EXISTS idx_analysis_history_nome_arquivo 
        ON analysis_history(nome_arquivo) WHERE nome_arquivo IS NOT NULL;
        
        CREATE INDEX IF NOT EXISTS idx_analysis_history_pontuacao 
        ON analysis_history(pontuacao_qualidade);
        
        -- Tabela para cache de análises (otimização)
        CREATE TABLE IF NOT EXISTS cache_analises (
            id SERIAL PRIMARY KEY,
            hash_codigo VARCHAR(64) UNIQUE NOT NULL,
            resultado JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            acessos INTEGER DEFAULT 1
        );
        
        -- Índice para o cache
        CREATE INDEX IF NOT EXISTS idx_cache_hash 
        ON cache_analises(hash_codigo);
        
        -- Tabela para estatísticas agregadas
        CREATE TABLE IF NOT EXISTS estatisticas_diarias (
            data DATE PRIMARY KEY,
            total_analises INTEGER DEFAULT 0,
            media_pontuacao DECIMAL(5,2),
            tempo_medio_analise DECIMAL(8,4),
            tipos_sugestoes_count JSONB,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.pool_conexoes.acquire() as conexao:
            await conexao.execute(sql_criar_tabelas)
            logger.info("Tabelas criadas/verificadas com sucesso!")
    
    async def salvar_analise(
        self,
        codigo: str,
        sugestoes: List[Sugestao],
        pontuacao: float,
        nome_arquivo: Optional[str] = None,
        tempo_analise: float = 0.0,
        nivel_detalhamento: str = "intermediario"
    ) -> int:
        """
        Salva uma análise no banco de dados.
        
        Args:
            codigo: Código analisado
            sugestoes: Lista de sugestões geradas
            pontuacao: Pontuação de qualidade
            nome_arquivo: Nome do arquivo (opcional)
            tempo_analise: Tempo gasto na análise
            nivel_detalhamento: Nível de detalhamento usado
            
        Returns:
            ID da análise salva
        """
        try:
            # Converte sugestões para JSON
            sugestoes_json = [sugestao.dict() for sugestao in sugestoes]
            
            # Conta tipos de sugestões
            tipos_sugestoes = {}
            for sugestao in sugestoes:
                tipo = sugestao.tipo.value
                tipos_sugestoes[tipo] = tipos_sugestoes.get(tipo, 0) + 1
            
            sql_inserir = """
            INSERT INTO analysis_history (
                code_snippet, suggestions, pontuacao_qualidade, 
                nome_arquivo, tempo_analise, nivel_detalhamento,
                numero_sugestoes, tipos_sugestoes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """
            
            async with self.pool_conexoes.acquire() as conexao:
                resultado = await conexao.fetchrow(
                    sql_inserir,
                    codigo,
                    json.dumps(sugestoes_json),
                    pontuacao,
                    nome_arquivo,
                    tempo_analise,
                    nivel_detalhamento,
                    len(sugestoes),
                    json.dumps(tipos_sugestoes)
                )
                
                analise_id = resultado['id']
                
                # Atualiza estatísticas diárias
                await self._atualizar_estatisticas_diarias(pontuacao, tempo_analise, tipos_sugestoes)
                
                logger.info(f"Análise salva com ID: {analise_id}")
                return analise_id
                
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {e}")
            raise
    
    async def obter_historico(
        self,
        limite: int = 10,
        offset: int = 0,
        nome_arquivo: Optional[str] = None
    ) -> List[HistoricoAnalise]:
        """
        Obtém o histórico de análises.
        
        Args:
            limite: Número máximo de registros
            offset: Número de registros a pular
            nome_arquivo: Filtrar por nome de arquivo
            
        Returns:
            Lista de análises do histórico
        """
        try:
            sql_base = """
            SELECT id, code_snippet, numero_sugestoes, pontuacao_qualidade,
                   nome_arquivo, created_at
            FROM analysis_history
            """
            
            parametros = []
            where_clause = ""
            
            if nome_arquivo:
                where_clause = " WHERE nome_arquivo = $1"
                parametros.append(nome_arquivo)
            
            sql_completo = f"""
            {sql_base}
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${len(parametros) + 1} OFFSET ${len(parametros) + 2}
            """
            
            parametros.extend([limite, offset])
            
            async with self.pool_conexoes.acquire() as conexao:
                registros = await conexao.fetch(sql_completo, *parametros)
                
                historico = []
                for registro in registros:
                    # Trunca o código para exibição
                    codigo_snippet = registro['code_snippet'][:200]
                    if len(registro['code_snippet']) > 200:
                        codigo_snippet += "..."
                    
                    historico.append(HistoricoAnalise(
                        id=registro['id'],
                        codigo_snippet=codigo_snippet,
                        numero_sugestoes=registro['numero_sugestoes'],
                        pontuacao_qualidade=float(registro['pontuacao_qualidade']),
                        nome_arquivo=registro['nome_arquivo'],
                        created_at=registro['created_at']
                    ))
                
                return historico
                
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            raise
    
    async def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais do sistema.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            sql_estatisticas = """
            SELECT 
                COUNT(*) as total_analises,
                AVG(pontuacao_qualidade) as media_pontuacao,
                AVG(tempo_analise) as tempo_medio_analise
            FROM analysis_history
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            """
            
            sql_tipos_sugestoes = """
            SELECT tipos_sugestoes
            FROM analysis_history
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            AND tipos_sugestoes IS NOT NULL
            """
            
            sql_analises_por_dia = """
            SELECT 
                DATE(created_at) as data,
                COUNT(*) as total
            FROM analysis_history
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY data DESC
            """
            
            async with self.pool_conexoes.acquire() as conexao:
                # Estatísticas gerais
                stats_gerais = await conexao.fetchrow(sql_estatisticas)
                
                # Tipos de sugestões mais comuns
                tipos_registros = await conexao.fetch(sql_tipos_sugestoes)
                tipos_consolidados = {}
                
                for registro in tipos_registros:
                    if registro['tipos_sugestoes']:
                        tipos_data = json.loads(registro['tipos_sugestoes'])
                        for tipo, count in tipos_data.items():
                            tipos_consolidados[tipo] = tipos_consolidados.get(tipo, 0) + count
                
                # Análises por dia
                analises_dia = await conexao.fetch(sql_analises_por_dia)
                analises_por_dia = {
                    str(registro['data']): registro['total']
                    for registro in analises_dia
                }
                
                return {
                    "total_analises": stats_gerais['total_analises'] or 0,
                    "media_pontuacao": float(stats_gerais['media_pontuacao'] or 0),
                    "tempo_medio_analise": float(stats_gerais['tempo_medio_analise'] or 0),
                    "tipos_sugestoes_mais_comuns": tipos_consolidados,
                    "analises_por_dia": analises_por_dia,
                    "periodo_estatisticas": "últimos 30 dias"
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise
    
    async def verificar_conexao(self) -> bool:
        """
        Verifica se a conexão com o banco está funcionando.
        
        Returns:
            True se a conexão está ok, False caso contrário
        """
        try:
            async with self.pool_conexoes.acquire() as conexao:
                await conexao.fetchval("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Erro na verificação de conexão: {e}")
            return False
    
    async def _atualizar_estatisticas_diarias(
        self,
        pontuacao: float,
        tempo_analise: float,
        tipos_sugestoes: Dict[str, int]
    ):
        """Atualiza as estatísticas diárias agregadas."""
        try:
            data_hoje = datetime.now().date()
            
            sql_upsert = """
            INSERT INTO estatisticas_diarias (
                data, total_analises, media_pontuacao, tempo_medio_analise, tipos_sugestoes_count
            ) VALUES ($1, 1, $2, $3, $4)
            ON CONFLICT (data) DO UPDATE SET
                total_analises = estatisticas_diarias.total_analises + 1,
                media_pontuacao = (
                    estatisticas_diarias.media_pontuacao * estatisticas_diarias.total_analises + $2
                ) / (estatisticas_diarias.total_analises + 1),
                tempo_medio_analise = (
                    estatisticas_diarias.tempo_medio_analise * estatisticas_diarias.total_analises + $3
                ) / (estatisticas_diarias.total_analises + 1),
                tipos_sugestoes_count = (
                    COALESCE(estatisticas_diarias.tipos_sugestoes_count, '{}'::jsonb) || $4::jsonb
                ),
                updated_at = CURRENT_TIMESTAMP
            """
            
            async with self.pool_conexoes.acquire() as conexao:
                await conexao.execute(
                    sql_upsert,
                    data_hoje,
                    pontuacao,
                    tempo_analise,
                    json.dumps(tipos_sugestoes)
                )
                
        except Exception as e:
            logger.warning(f"Erro ao atualizar estatísticas diárias: {e}")
            # Não propaga o erro para não afetar a operação principal
    
    async def fechar_conexoes(self):
        """Fecha todas as conexões com o banco de dados."""
        try:
            if self.pool_conexoes:
                await self.pool_conexoes.close()
                logger.info("Conexões com banco de dados fechadas")
        except Exception as e:
            logger.error(f"Erro ao fechar conexões: {e}")
    
    async def limpar_cache_antigo(self, dias: int = 7):
        """
        Remove entradas antigas do cache.
        
        Args:
            dias: Número de dias para manter no cache
        """
        try:
            sql_limpar = """
            DELETE FROM cache_analises 
            WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """
            
            async with self.pool_conexoes.acquire() as conexao:
                resultado = await conexao.execute(sql_limpar, dias)
                logger.info(f"Cache limpo: {resultado} entradas removidas")
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    async def obter_analise_por_id(self, analise_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém uma análise específica por ID.
        
        Args:
            analise_id: ID da análise
            
        Returns:
            Dados da análise ou None se não encontrada
        """
        try:
            sql_buscar = """
            SELECT * FROM analysis_history WHERE id = $1
            """
            
            async with self.pool_conexoes.acquire() as conexao:
                registro = await conexao.fetchrow(sql_buscar, analise_id)
                
                if registro:
                    return dict(registro)
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar análise {analise_id}: {e}")
            raise

