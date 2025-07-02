"""
Configuração do Banco de Dados PostgreSQL.

Define as configurações de conexão e parâmetros do banco de dados
para o agente de otimização de código.
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class ConfiguracaoBancoDados:
    """
    Configurações para conexão com PostgreSQL.
    
    Utiliza variáveis de ambiente quando disponíveis,
    com valores padrão para desenvolvimento local.
    """
    
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    porta: int = int(os.getenv("POSTGRES_PORT", "5432"))
    nome_banco: str = os.getenv("POSTGRES_DB", "agente_otimizacao")
    usuario: str = os.getenv("POSTGRES_USER", "postgres")
    senha: str = os.getenv("POSTGRES_PASSWORD", "postgres123")
    
    # Configurações do pool de conexões
    min_conexoes: int = int(os.getenv("DB_MIN_CONNECTIONS", "2"))
    max_conexoes: int = int(os.getenv("DB_MAX_CONNECTIONS", "10"))
    
    # Configurações de timeout
    timeout_conexao: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    timeout_comando: int = int(os.getenv("DB_COMMAND_TIMEOUT", "60"))
    
    @property
    def url_conexao(self) -> str:
        """Retorna a URL de conexão PostgreSQL."""
        return f"postgresql://{self.usuario}:{self.senha}@{self.host}:{self.porta}/{self.nome_banco}"
    
    @property
    def url_conexao_async(self) -> str:
        """Retorna a URL de conexão PostgreSQL para uso assíncrono."""
        return f"postgresql+asyncpg://{self.usuario}:{self.senha}@{self.host}:{self.porta}/{self.nome_banco}"
    
    def validar_configuracao(self) -> bool:
        """
        Valida se todas as configurações necessárias estão presentes.
        
        Returns:
            True se a configuração é válida, False caso contrário
        """
        campos_obrigatorios = [
            self.host, self.nome_banco, self.usuario, self.senha
        ]
        
        return all(campo for campo in campos_obrigatorios)
    
    def __str__(self) -> str:
        """Representação string da configuração (sem senha)."""
        return (
            f"ConfiguracaoBancoDados("
            f"host={self.host}, "
            f"porta={self.porta}, "
            f"banco={self.nome_banco}, "
            f"usuario={self.usuario}, "
            f"pool={self.min_conexoes}-{self.max_conexoes})"
        )

