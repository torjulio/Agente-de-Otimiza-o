"""
Agente de Otimização de Código Python
Desenvolvido para o Desafio Técnico da Mirante Tecnologia

Este agente fornece sugestões de otimização de código Python
baseadas em boas práticas e padrões de qualidade.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import logging

from servicos.analisador_codigo import AnalisadorCodigo
from servicos.banco_dados import GerenciadorBancoDados
from modelos.schemas import (
    SolicitacaoAnalise,
    RespostaAnalise,
    StatusSaude,
    HistoricoAnalise
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização da aplicação
app = FastAPI(
    title="Agente de Otimização de Código Python",
    description="API para análise e otimização de código Python com sugestões baseadas em boas práticas",
    version="1.0.0",
    docs_url="/documentacao",
    redoc_url="/documentacao-redoc"
)

# Configuração CORS para permitir acesso de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias dos serviços
analisador = AnalisadorCodigo()
gerenciador_bd = GerenciadorBancoDados()

@app.on_event("startup")
async def inicializar_aplicacao():
    """Inicializa a aplicação e configura o banco de dados."""
    logger.info("Iniciando Agente de Otimização de Código...")
    await gerenciador_bd.inicializar_banco()
    logger.info("Aplicação iniciada com sucesso!")

@app.on_event("shutdown")
async def finalizar_aplicacao():
    """Finaliza a aplicação e fecha conexões."""
    logger.info("Finalizando aplicação...")
    await gerenciador_bd.fechar_conexoes()
    logger.info("Aplicação finalizada!")

@app.get("/health", response_model=StatusSaude, tags=["Saúde"])
async def verificar_saude():
    """
    Endpoint para verificar o status de saúde do agente.
    
    Returns:
        StatusSaude: Status atual do agente e seus componentes
    """
    try:
        # Verifica conexão com banco de dados
        status_bd = await gerenciador_bd.verificar_conexao()
        
        return StatusSaude(
            status="ok",
            timestamp=datetime.now(),
            versao="1.0.0",
            banco_dados=status_bd,
            servicos_ativos=["analisador_codigo", "banco_dados"]
        )
    except Exception as e:
        logger.error(f"Erro ao verificar saúde: {e}")
        raise HTTPException(status_code=503, detail="Serviço indisponível")

@app.post("/analyze-code", response_model=RespostaAnalise, tags=["Análise"])
async def analisar_codigo(solicitacao: SolicitacaoAnalise):
    """
    Endpoint principal para análise de código Python.
    
    Args:
        solicitacao: Dados da solicitação contendo o código a ser analisado
        
    Returns:
        RespostaAnalise: Sugestões de otimização e melhorias
    """
    try:
        logger.info(f"Iniciando análise de código para: {solicitacao.nome_arquivo or 'código anônimo'}")
        
        # Realiza a análise do código
        sugestoes = await analisador.analisar_codigo(
            codigo=solicitacao.codigo,
            nivel_detalhamento=solicitacao.nivel_detalhamento,
            focar_performance=solicitacao.focar_performance
        )
        
        # Prepara a resposta
        resposta = RespostaAnalise(
            codigo_original=solicitacao.codigo,
            sugestoes=sugestoes,
            pontuacao_qualidade=analisador.calcular_pontuacao_qualidade(solicitacao.codigo),
            tempo_analise=analisador.ultimo_tempo_analise,
            timestamp=datetime.now()
        )
        
        # Salva no histórico
        await gerenciador_bd.salvar_analise(
            codigo=solicitacao.codigo,
            sugestoes=sugestoes,
            pontuacao=resposta.pontuacao_qualidade,
            nome_arquivo=solicitacao.nome_arquivo
        )
        
        logger.info("Análise concluída com sucesso!")
        return resposta
        
    except Exception as e:
        logger.error(f"Erro durante análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/historico", response_model=List[HistoricoAnalise], tags=["Histórico"])
async def obter_historico(
    limite: int = 10,
    offset: int = 0,
    nome_arquivo: Optional[str] = None
):
    """
    Obtém o histórico de análises realizadas.
    
    Args:
        limite: Número máximo de registros a retornar
        offset: Número de registros a pular
        nome_arquivo: Filtrar por nome de arquivo específico
        
    Returns:
        List[HistoricoAnalise]: Lista de análises realizadas
    """
    try:
        historico = await gerenciador_bd.obter_historico(
            limite=limite,
            offset=offset,
            nome_arquivo=nome_arquivo
        )
        return historico
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail="Erro ao acessar histórico")

@app.get("/estatisticas", tags=["Estatísticas"])
async def obter_estatisticas():
    """
    Obtém estatísticas gerais sobre as análises realizadas.
    
    Returns:
        dict: Estatísticas do sistema
    """
    try:
        stats = await gerenciador_bd.obter_estatisticas()
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao acessar estatísticas")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

