"""
Modelos de dados para o Agente de Otimização de Código.

Define as estruturas de dados utilizadas na API para
solicitações, respostas e armazenamento no banco de dados.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NivelDetalhamento(str, Enum):
    """Níveis de detalhamento para análise de código."""
    BASICO = "basico"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"

class TipoSugestao(str, Enum):
    """Tipos de sugestões de otimização."""
    PERFORMANCE = "performance"
    LEGIBILIDADE = "legibilidade"
    BOAS_PRATICAS = "boas_praticas"
    SEGURANCA = "seguranca"
    MANUTENCAO = "manutencao"

class SolicitacaoAnalise(BaseModel):
    """Modelo para solicitação de análise de código."""
    
    codigo: str = Field(
        ...,
        description="Código Python a ser analisado",
        min_length=1,
        max_length=50000
    )
    
    nome_arquivo: Optional[str] = Field(
        None,
        description="Nome do arquivo (opcional)",
        max_length=255
    )
    
    nivel_detalhamento: NivelDetalhamento = Field(
        default=NivelDetalhamento.INTERMEDIARIO,
        description="Nível de detalhamento da análise"
    )
    
    focar_performance: bool = Field(
        default=False,
        description="Focar especificamente em otimizações de performance"
    )
    
    @validator('codigo')
    def validar_codigo(cls, v):
        """Valida se o código não está vazio e contém Python válido."""
        if not v.strip():
            raise ValueError("Código não pode estar vazio")
        
        # Verificação básica de sintaxe Python
        try:
            compile(v, '<string>', 'exec')
        except SyntaxError as e:
            raise ValueError(f"Erro de sintaxe no código: {e}")
        
        return v

class Sugestao(BaseModel):
    """Modelo para uma sugestão individual de otimização."""
    
    tipo: TipoSugestao = Field(
        ...,
        description="Tipo da sugestão"
    )
    
    titulo: str = Field(
        ...,
        description="Título resumido da sugestão",
        max_length=200
    )
    
    descricao: str = Field(
        ...,
        description="Descrição detalhada da sugestão"
    )
    
    linha_inicio: Optional[int] = Field(
        None,
        description="Linha onde o problema foi identificado",
        ge=1
    )
    
    linha_fim: Optional[int] = Field(
        None,
        description="Linha final do problema (para blocos)",
        ge=1
    )
    
    codigo_original: Optional[str] = Field(
        None,
        description="Trecho de código original com problema"
    )
    
    codigo_sugerido: Optional[str] = Field(
        None,
        description="Código sugerido como melhoria"
    )
    
    impacto: str = Field(
        ...,
        description="Impacto da implementação (baixo, médio, alto)"
    )
    
    prioridade: int = Field(
        ...,
        description="Prioridade da sugestão (1-10)",
        ge=1,
        le=10
    )

class RespostaAnalise(BaseModel):
    """Modelo para resposta da análise de código."""
    
    codigo_original: str = Field(
        ...,
        description="Código original analisado"
    )
    
    sugestoes: List[Sugestao] = Field(
        ...,
        description="Lista de sugestões de otimização"
    )
    
    pontuacao_qualidade: float = Field(
        ...,
        description="Pontuação de qualidade do código (0-100)",
        ge=0,
        le=100
    )
    
    tempo_analise: float = Field(
        ...,
        description="Tempo gasto na análise em segundos",
        ge=0
    )
    
    timestamp: datetime = Field(
        ...,
        description="Timestamp da análise"
    )
    
    resumo_melhorias: Optional[str] = Field(
        None,
        description="Resumo das principais melhorias sugeridas"
    )

class StatusSaude(BaseModel):
    """Modelo para status de saúde do sistema."""
    
    status: str = Field(
        ...,
        description="Status geral do sistema"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Timestamp da verificação"
    )
    
    versao: str = Field(
        ...,
        description="Versão da aplicação"
    )
    
    banco_dados: bool = Field(
        ...,
        description="Status da conexão com banco de dados"
    )
    
    servicos_ativos: List[str] = Field(
        ...,
        description="Lista de serviços ativos"
    )

class HistoricoAnalise(BaseModel):
    """Modelo para histórico de análises."""
    
    id: int = Field(
        ...,
        description="ID único da análise"
    )
    
    codigo_snippet: str = Field(
        ...,
        description="Trecho do código analisado"
    )
    
    numero_sugestoes: int = Field(
        ...,
        description="Número de sugestões geradas"
    )
    
    pontuacao_qualidade: float = Field(
        ...,
        description="Pontuação de qualidade obtida"
    )
    
    nome_arquivo: Optional[str] = Field(
        None,
        description="Nome do arquivo analisado"
    )
    
    created_at: datetime = Field(
        ...,
        description="Data e hora da análise"
    )

class ConfiguracaoCrewAI(BaseModel):
    """Configuração para integração com Crew AI."""
    
    nome_agente: str = Field(
        default="otimizador_codigo_python",
        description="Nome do agente no Crew AI"
    )
    
    descricao_agente: str = Field(
        default="Especialista em otimização de código Python",
        description="Descrição do agente"
    )
    
    habilidades: List[str] = Field(
        default=[
            "analise_codigo_python",
            "otimizacao_performance",
            "boas_praticas_programacao",
            "refatoracao_codigo"
        ],
        description="Lista de habilidades do agente"
    )
    
    workflow_id: Optional[str] = Field(
        None,
        description="ID do workflow no Crew AI"
    )

class EstatisticasGerais(BaseModel):
    """Estatísticas gerais do sistema."""
    
    total_analises: int = Field(
        ...,
        description="Total de análises realizadas"
    )
    
    media_pontuacao: float = Field(
        ...,
        description="Média de pontuação de qualidade"
    )
    
    tipos_sugestoes_mais_comuns: Dict[str, int] = Field(
        ...,
        description="Tipos de sugestões mais frequentes"
    )
    
    tempo_medio_analise: float = Field(
        ...,
        description="Tempo médio de análise em segundos"
    )
    
    analises_por_dia: Dict[str, int] = Field(
        ...,
        description="Número de análises por dia (últimos 30 dias)"
    )

