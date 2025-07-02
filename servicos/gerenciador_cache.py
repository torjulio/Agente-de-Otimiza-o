"""
Gerenciador de Cache para Escalabilidade.

Implementa sistema de cache distribuído usando Redis para melhorar
a performance e escalabilidade do agente de otimização.
"""

import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import pickle

try:
    import redis.asyncio as redis
    REDIS_DISPONIVEL = True
except ImportError:
    REDIS_DISPONIVEL = False
    redis = None

from configuracao.configuracao_bd import ConfiguracaoBancoDados

logger = logging.getLogger(__name__)

class GerenciadorCache:
    """
    Gerenciador de cache distribuído para otimização de performance.
    
    Utiliza Redis como backend de cache com fallback para cache em memória
    quando Redis não estiver disponível.
    """
    
    def __init__(self):
        self.redis_client = None
        self.cache_local = {}  # Fallback para cache em memória
        self.config = self._carregar_configuracao_cache()
        self.estatisticas = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'inicio': datetime.now()
        }
    
    def _carregar_configuracao_cache(self) -> Dict[str, Any]:
        """Carrega configurações do cache."""
        return {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'ttl_padrao': 3600,  # 1 hora
            'ttl_analises': 7200,  # 2 horas
            'ttl_estatisticas': 300,  # 5 minutos
            'max_cache_local': 1000,  # Máximo de itens no cache local
            'prefixo_chaves': 'agente_otimizacao:'
        }
    
    async def inicializar(self):
        """Inicializa a conexão com Redis."""
        if not REDIS_DISPONIVEL:
            logger.warning("Redis não disponível, usando cache em memória")
            return
        
        try:
            self.redis_client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db'],
                decode_responses=False,  # Para suportar pickle
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Testa a conexão
            await self.redis_client.ping()
            logger.info("Cache Redis inicializado com sucesso")
            
        except Exception as e:
            logger.warning(f"Falha ao conectar com Redis: {e}. Usando cache local.")
            self.redis_client = None
    
    def _gerar_chave_cache(self, namespace: str, identificador: str) -> str:
        """Gera chave única para o cache."""
        chave_base = f"{self.config['prefixo_chaves']}{namespace}:{identificador}"
        return chave_base
    
    def _gerar_hash_codigo(self, codigo: str) -> str:
        """Gera hash único para um código."""
        return hashlib.sha256(codigo.encode('utf-8')).hexdigest()[:16]
    
    async def obter_analise_cache(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtém análise do cache baseada no código.
        
        Args:
            codigo: Código Python para buscar no cache
            
        Returns:
            Resultado da análise se encontrado no cache, None caso contrário
        """
        hash_codigo = self._gerar_hash_codigo(codigo)
        chave = self._gerar_chave_cache("analise", hash_codigo)
        
        try:
            resultado = await self._obter_do_cache(chave)
            if resultado:
                self.estatisticas['hits'] += 1
                logger.debug(f"Cache hit para análise: {hash_codigo}")
                return resultado
            else:
                self.estatisticas['misses'] += 1
                logger.debug(f"Cache miss para análise: {hash_codigo}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {e}")
            self.estatisticas['misses'] += 1
            return None
    
    async def salvar_analise_cache(
        self,
        codigo: str,
        resultado_analise: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """
        Salva resultado de análise no cache.
        
        Args:
            codigo: Código Python analisado
            resultado_analise: Resultado da análise
            ttl: Tempo de vida em segundos (opcional)
        """
        hash_codigo = self._gerar_hash_codigo(codigo)
        chave = self._gerar_chave_cache("analise", hash_codigo)
        ttl_final = ttl or self.config['ttl_analises']
        
        # Adiciona metadados ao resultado
        dados_cache = {
            'resultado': resultado_analise,
            'timestamp': datetime.now().isoformat(),
            'hash_codigo': hash_codigo,
            'tamanho_codigo': len(codigo)
        }
        
        try:
            await self._salvar_no_cache(chave, dados_cache, ttl_final)
            self.estatisticas['sets'] += 1
            logger.debug(f"Análise salva no cache: {hash_codigo}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no cache: {e}")
    
    async def obter_estatisticas_cache(self) -> Optional[Dict[str, Any]]:
        """Obtém estatísticas do sistema do cache."""
        chave = self._gerar_chave_cache("stats", "sistema")
        
        try:
            return await self._obter_do_cache(chave)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return None
    
    async def salvar_estatisticas_cache(self, estatisticas: Dict[str, Any]):
        """Salva estatísticas do sistema no cache."""
        chave = self._gerar_chave_cache("stats", "sistema")
        ttl = self.config['ttl_estatisticas']
        
        try:
            await self._salvar_no_cache(chave, estatisticas, ttl)
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas no cache: {e}")
    
    async def invalidar_cache_usuario(self, identificador_usuario: str):
        """Invalida todo o cache relacionado a um usuário específico."""
        padrao = self._gerar_chave_cache("user", f"{identificador_usuario}:*")
        
        try:
            if self.redis_client:
                chaves = await self.redis_client.keys(padrao)
                if chaves:
                    await self.redis_client.delete(*chaves)
                    self.estatisticas['deletes'] += len(chaves)
                    logger.info(f"Invalidadas {len(chaves)} chaves do usuário {identificador_usuario}")
            else:
                # Cache local - remove chaves que começam com o padrão
                chaves_remover = [
                    k for k in self.cache_local.keys()
                    if k.startswith(padrao.replace('*', ''))
                ]
                for chave in chaves_remover:
                    del self.cache_local[chave]
                self.estatisticas['deletes'] += len(chaves_remover)
                
        except Exception as e:
            logger.error(f"Erro ao invalidar cache do usuário: {e}")
    
    async def limpar_cache_expirado(self):
        """Remove entradas expiradas do cache local."""
        if self.redis_client:
            # Redis gerencia expiração automaticamente
            return
        
        agora = datetime.now()
        chaves_expiradas = []
        
        for chave, dados in self.cache_local.items():
            if isinstance(dados, dict) and 'expira_em' in dados:
                if agora > dados['expira_em']:
                    chaves_expiradas.append(chave)
        
        for chave in chaves_expiradas:
            del self.cache_local[chave]
        
        if chaves_expiradas:
            logger.info(f"Removidas {len(chaves_expiradas)} entradas expiradas do cache local")
    
    async def obter_info_cache(self) -> Dict[str, Any]:
        """Obtém informações detalhadas sobre o cache."""
        info = {
            'tipo_cache': 'redis' if self.redis_client else 'local',
            'estatisticas': self.estatisticas.copy(),
            'configuracao': self.config.copy()
        }
        
        # Calcula taxa de acerto
        total_acessos = self.estatisticas['hits'] + self.estatisticas['misses']
        if total_acessos > 0:
            info['taxa_acerto'] = (self.estatisticas['hits'] / total_acessos) * 100
        else:
            info['taxa_acerto'] = 0
        
        # Informações específicas do Redis
        if self.redis_client:
            try:
                info_redis = await self.redis_client.info()
                info['redis_info'] = {
                    'memoria_usada': info_redis.get('used_memory_human'),
                    'conexoes_ativas': info_redis.get('connected_clients'),
                    'comandos_processados': info_redis.get('total_commands_processed'),
                    'uptime': info_redis.get('uptime_in_seconds')
                }
            except Exception as e:
                logger.warning(f"Erro ao obter info do Redis: {e}")
        else:
            # Informações do cache local
            info['cache_local_info'] = {
                'total_itens': len(self.cache_local),
                'limite_maximo': self.config['max_cache_local'],
                'uso_percentual': (len(self.cache_local) / self.config['max_cache_local']) * 100
            }
        
        return info
    
    async def _obter_do_cache(self, chave: str) -> Optional[Any]:
        """Obtém valor do cache (Redis ou local)."""
        if self.redis_client:
            try:
                dados_bytes = await self.redis_client.get(chave)
                if dados_bytes:
                    return pickle.loads(dados_bytes)
                return None
            except Exception as e:
                logger.error(f"Erro ao obter do Redis: {e}")
                return None
        else:
            # Cache local
            dados = self.cache_local.get(chave)
            if dados and isinstance(dados, dict):
                # Verifica expiração
                if 'expira_em' in dados and datetime.now() > dados['expira_em']:
                    del self.cache_local[chave]
                    return None
                return dados.get('valor')
            return dados
    
    async def _salvar_no_cache(self, chave: str, valor: Any, ttl: int):
        """Salva valor no cache (Redis ou local)."""
        if self.redis_client:
            try:
                dados_bytes = pickle.dumps(valor)
                await self.redis_client.setex(chave, ttl, dados_bytes)
            except Exception as e:
                logger.error(f"Erro ao salvar no Redis: {e}")
                # Fallback para cache local
                await self._salvar_cache_local(chave, valor, ttl)
        else:
            await self._salvar_cache_local(chave, valor, ttl)
    
    async def _salvar_cache_local(self, chave: str, valor: Any, ttl: int):
        """Salva valor no cache local."""
        # Verifica limite do cache local
        if len(self.cache_local) >= self.config['max_cache_local']:
            # Remove item mais antigo (FIFO simples)
            chave_mais_antiga = next(iter(self.cache_local))
            del self.cache_local[chave_mais_antiga]
        
        expira_em = datetime.now() + timedelta(seconds=ttl)
        self.cache_local[chave] = {
            'valor': valor,
            'expira_em': expira_em
        }
    
    async def fechar_conexoes(self):
        """Fecha conexões do cache."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Conexão Redis fechada")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão Redis: {e}")
        
        # Limpa cache local
        self.cache_local.clear()

# Instância global do gerenciador de cache
gerenciador_cache = GerenciadorCache()

