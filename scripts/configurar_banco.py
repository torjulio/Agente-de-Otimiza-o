#!/usr/bin/env python3
"""
Este script configura o banco PostgreSQL para o agente de otimização,
criando o banco de dados, usuário e tabelas necessárias.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncpg
from configuracao.configuracao_bd import ConfiguracaoBancoDados

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def criar_banco_se_nao_existir():
    """Cria o banco de dados se ele não existir."""
    config = ConfiguracaoBancoDados()
    
    try:
        conexao = await asyncpg.connect(
            host=config.host,
            port=config.porta,
            user=config.usuario,
            password=config.senha,
            database='postgres'
        )
        
        # Verifica se o banco já existe
        resultado = await conexao.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            config.nome_banco
        )
        
        if not resultado:
            logger.info(f"Criando banco de dados '{config.nome_banco}'...")
            await conexao.execute(f'CREATE DATABASE "{config.nome_banco}"')
            logger.info("Banco de dados criado com sucesso!")
        else:
            logger.info(f"Banco de dados '{config.nome_banco}' já existe.")
        
        await conexao.close()
        
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        raise

async def criar_tabelas():
    """Cria todas as tabelas necessárias."""
    config = ConfiguracaoBancoDados()
    
    sql_tabelas = """
    -- Extensões necessárias
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Tabela principal para histórico de análises
    CREATE TABLE IF NOT EXISTS analysis_history (
        id SERIAL PRIMARY KEY,
        code_snippet TEXT NOT NULL,
        suggestions JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        pontuacao_qualidade DECIMAL(5,2) CHECK (pontuacao_qualidade >= 0 AND pontuacao_qualidade <= 100),
        nome_arquivo VARCHAR(255),
        tempo_analise DECIMAL(8,4) CHECK (tempo_analise >= 0),
        nivel_detalhamento VARCHAR(20) CHECK (nivel_detalhamento IN ('basico', 'intermediario', 'avancado')),
        numero_sugestoes INTEGER DEFAULT 0 CHECK (numero_sugestoes >= 0),
        tipos_sugestoes JSONB,
        hash_codigo VARCHAR(64),
        tamanho_codigo INTEGER
    );
    
    -- Índices para melhor performance
    CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
    ON analysis_history(created_at DESC);
    
    CREATE INDEX IF NOT EXISTS idx_analysis_history_nome_arquivo 
    ON analysis_history(nome_arquivo) WHERE nome_arquivo IS NOT NULL;
    
    CREATE INDEX IF NOT EXISTS idx_analysis_history_pontuacao 
    ON analysis_history(pontuacao_qualidade DESC);
    
    CREATE INDEX IF NOT EXISTS idx_analysis_history_hash 
    ON analysis_history(hash_codigo) WHERE hash_codigo IS NOT NULL;
    
    -- Tabela para cache de análises (otimização de performance)
    CREATE TABLE IF NOT EXISTS cache_analises (
        id SERIAL PRIMARY KEY,
        hash_codigo VARCHAR(64) UNIQUE NOT NULL,
        resultado JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        acessos INTEGER DEFAULT 1,
        ultimo_acesso TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Índices para o cache
    CREATE INDEX IF NOT EXISTS idx_cache_hash 
    ON cache_analises(hash_codigo);
    
    CREATE INDEX IF NOT EXISTS idx_cache_ultimo_acesso 
    ON cache_analises(ultimo_acesso);
    
    -- Tabela para estatísticas agregadas por dia
    CREATE TABLE IF NOT EXISTS estatisticas_diarias (
        data DATE PRIMARY KEY,
        total_analises INTEGER DEFAULT 0,
        media_pontuacao DECIMAL(5,2),
        tempo_medio_analise DECIMAL(8,4),
        tipos_sugestoes_count JSONB,
        arquivos_unicos INTEGER DEFAULT 0,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabela para configurações do sistema
    CREATE TABLE IF NOT EXISTS configuracoes_sistema (
        chave VARCHAR(100) PRIMARY KEY,
        valor JSONB NOT NULL,
        descricao TEXT,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabela para logs de auditoria
    CREATE TABLE IF NOT EXISTS logs_auditoria (
        id SERIAL PRIMARY KEY,
        acao VARCHAR(50) NOT NULL,
        detalhes JSONB,
        ip_origem INET,
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Índice para logs de auditoria
    CREATE INDEX IF NOT EXISTS idx_logs_auditoria_created_at 
    ON logs_auditoria(created_at DESC);
    
    -- Função para atualizar timestamp automaticamente
    CREATE OR REPLACE FUNCTION atualizar_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    -- Triggers para atualização automática de timestamps
    DROP TRIGGER IF EXISTS trigger_estatisticas_updated_at ON estatisticas_diarias;
    CREATE TRIGGER trigger_estatisticas_updated_at
        BEFORE UPDATE ON estatisticas_diarias
        FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
    
    DROP TRIGGER IF EXISTS trigger_configuracoes_updated_at ON configuracoes_sistema;
    CREATE TRIGGER trigger_configuracoes_updated_at
        BEFORE UPDATE ON configuracoes_sistema
        FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
    """
    
    try:
        conexao = await asyncpg.connect(
            host=config.host,
            port=config.porta,
            user=config.usuario,
            password=config.senha,
            database=config.nome_banco
        )
        
        logger.info("Criando tabelas e índices...")
        await conexao.execute(sql_tabelas)
        logger.info("Tabelas criadas com sucesso!")
        
        await conexao.close()
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise

async def inserir_dados_iniciais():
    """Insere dados iniciais e configurações padrão."""
    config = ConfiguracaoBancoDados()
    
    configuracoes_iniciais = [
        {
            'chave': 'versao_schema',
            'valor': '{"versao": "1.0.0", "data_criacao": "2024-01-01"}',
            'descricao': 'Versão do schema do banco de dados'
        },
        {
            'chave': 'configuracao_cache',
            'valor': '{"ttl_dias": 7, "max_entradas": 10000, "limpeza_automatica": true}',
            'descricao': 'Configurações do sistema de cache'
        },
        {
            'chave': 'limites_analise',
            'valor': '{"max_codigo_tamanho": 50000, "timeout_analise": 30, "max_sugestoes": 50}',
            'descricao': 'Limites para análise de código'
        }
    ]
    
    try:
        conexao = await asyncpg.connect(
            host=config.host,
            port=config.porta,
            user=config.usuario,
            password=config.senha,
            database=config.nome_banco
        )
        
        logger.info("Inserindo configurações iniciais...")
        
        for config_item in configuracoes_iniciais:
            await conexao.execute(
                """
                INSERT INTO configuracoes_sistema (chave, valor, descricao)
                VALUES ($1, $2, $3)
                ON CONFLICT (chave) DO NOTHING
                """,
                config_item['chave'],
                config_item['valor'],
                config_item['descricao']
            )
        
        logger.info("Configurações iniciais inseridas!")
        await conexao.close()
        
    except Exception as e:
        logger.error(f"Erro ao inserir dados iniciais: {e}")
        raise

async def verificar_conexao():
    """Verifica se a conexão com o banco está funcionando."""
    config = ConfiguracaoBancoDados()
    
    try:
        conexao = await asyncpg.connect(
            host=config.host,
            port=config.porta,
            user=config.usuario,
            password=config.senha,
            database=config.nome_banco
        )
        
        # Testa uma consulta simples
        resultado = await conexao.fetchval("SELECT version()")
        logger.info(f"Conexão bem-sucedida! PostgreSQL: {resultado}")
        
        tabelas = await conexao.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        
        logger.info(f"Tabelas encontradas: {[t['table_name'] for t in tabelas]}")
        
        await conexao.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação de conexão: {e}")
        return False

async def main():
    """Função principal do script de configuração."""
    logger.info("=== Configuração do Banco de Dados ===")
    
    config = ConfiguracaoBancoDados()
    logger.info(f"Configuração: {config}")
    
    if not config.validar_configuracao():
        logger.error("Configuração inválida! Verifique as variáveis de ambiente.")
        sys.exit(1)
    
    try:
        await criar_banco_se_nao_existir()
        
        await criar_tabelas()

        await inserir_dados_iniciais()
        
        #  Verifica se tudo está funcionando
        if await verificar_conexao():
            logger.info("✅ Configuração do banco concluída com sucesso!")
        else:
            logger.error("❌ Falha na verificação final!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro durante configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

