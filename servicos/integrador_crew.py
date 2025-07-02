"""
Integrador Crew AI.

Conecta o agente principal de otimização com o sistema de orquestração
Crew AI, permitindo workflows complexos e colaboração entre agentes.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from servicos.orquestrador_crew import OrquestradorCrewAI
from servicos.analisador_codigo import AnalisadorCodigo
from modelos.schemas import SolicitacaoAnalise, RespostaAnalise, Sugestao, TipoSugestao

logger = logging.getLogger(__name__)

class IntegradorCrewAI:
    """
    Integrador principal entre o agente de otimização e o Crew AI.
    
    Coordena a execução de workflows complexos utilizando múltiplos
    agentes especializados para análise abrangente de código.
    """
    
    def __init__(self):
        self.orquestrador = OrquestradorCrewAI()
        self.analisador_local = AnalisadorCodigo()
        self.workflows_em_execucao = {}
    
    async def analisar_com_crew_ai(
        self,
        solicitacao: SolicitacaoAnalise,
        usar_workflow_completo: bool = True
    ) -> RespostaAnalise:
        """
        Executa análise de código usando orquestração Crew AI.
        
        Args:
            solicitacao: Dados da solicitação de análise
            usar_workflow_completo: Se deve usar workflow completo ou análise simples
            
        Returns:
            Resposta com análise completa do código
        """
        inicio_tempo = datetime.now()
        
        try:
            if usar_workflow_completo:
                # Executa workflow completo com múltiplos agentes
                resultado = await self._executar_workflow_completo(solicitacao)
            else:
                # Executa análise simples com agente local
                resultado = await self._executar_analise_simples(solicitacao)
            
            # Converte resultado para formato padrão da API
            resposta = await self._converter_resultado_para_resposta(
                resultado, solicitacao, inicio_tempo
            )
            
            logger.info(f"Análise Crew AI concluída em {resposta.tempo_analise:.2f}s")
            return resposta
            
        except Exception as e:
            logger.error(f"Erro na análise Crew AI: {e}")
            # Fallback para análise local em caso de erro
            return await self._executar_fallback_local(solicitacao)
    
    async def _executar_workflow_completo(
        self,
        solicitacao: SolicitacaoAnalise
    ) -> Dict[str, Any]:
        """Executa workflow completo com orquestração Crew AI."""
        
        # Define prioridades baseadas na solicitação
        prioridades = self._determinar_prioridades(solicitacao)
        
        # Cria workflow
        workflow_id = await self.orquestrador.criar_workflow_otimizacao(
            codigo=solicitacao.codigo,
            nome_arquivo=solicitacao.nome_arquivo,
            prioridades=prioridades
        )
        
        # Registra workflow em execução
        self.workflows_em_execucao[workflow_id] = {
            'solicitacao': solicitacao,
            'inicio': datetime.now(),
            'status': 'executando'
        }
        
        try:
            # Executa workflow
            resultado = await self.orquestrador.executar_workflow(workflow_id)
            
            # Atualiza status
            self.workflows_em_execucao[workflow_id]['status'] = 'concluido'
            self.workflows_em_execucao[workflow_id]['resultado'] = resultado
            
            return resultado
            
        except Exception as e:
            self.workflows_em_execucao[workflow_id]['status'] = 'erro'
            self.workflows_em_execucao[workflow_id]['erro'] = str(e)
            raise
    
    async def _executar_analise_simples(
        self,
        solicitacao: SolicitacaoAnalise
    ) -> Dict[str, Any]:
        """Executa análise simples usando apenas o agente local."""
        
        sugestoes = await self.analisador_local.analisar_codigo(
            codigo=solicitacao.codigo,
            nivel_detalhamento=solicitacao.nivel_detalhamento,
            focar_performance=solicitacao.focar_performance
        )
        
        return {
            'tipo_execucao': 'analise_simples',
            'sugestoes': sugestoes,
            'pontuacao_qualidade': self.analisador_local.calcular_pontuacao_qualidade(
                solicitacao.codigo
            ),
            'agente_executor': 'analisador_local'
        }
    
    def _determinar_prioridades(self, solicitacao: SolicitacaoAnalise) -> List[str]:
        """Determina prioridades de análise baseadas na solicitação."""
        prioridades = []
        
        if solicitacao.focar_performance:
            prioridades.append("performance")
        
        # Sempre inclui boas práticas para análise completa
        prioridades.extend(["boas_praticas", "seguranca"])
        
        # Adiciona prioridades baseadas no nível de detalhamento
        if solicitacao.nivel_detalhamento.value == "avancado":
            prioridades.extend(["complexidade", "manutencao"])
        
        return prioridades
    
    async def _converter_resultado_para_resposta(
        self,
        resultado: Dict[str, Any],
        solicitacao: SolicitacaoAnalise,
        inicio_tempo: datetime
    ) -> RespostaAnalise:
        """Converte resultado do Crew AI para formato da API."""
        
        tempo_analise = (datetime.now() - inicio_tempo).total_seconds()
        
        if resultado.get('tipo_execucao') == 'analise_simples':
            # Resultado de análise simples
            sugestoes = resultado['sugestoes']
            pontuacao = resultado['pontuacao_qualidade']
        else:
            # Resultado de workflow completo
            sugestoes = await self._extrair_sugestoes_do_workflow(resultado)
            pontuacao = self._calcular_pontuacao_do_workflow(resultado)
        
        # Gera resumo das melhorias
        resumo = self._gerar_resumo_melhorias(sugestoes)
        
        return RespostaAnalise(
            codigo_original=solicitacao.codigo,
            sugestoes=sugestoes,
            pontuacao_qualidade=pontuacao,
            tempo_analise=tempo_analise,
            timestamp=datetime.now(),
            resumo_melhorias=resumo
        )
    
    async def _extrair_sugestoes_do_workflow(
        self,
        resultado_workflow: Dict[str, Any]
    ) -> List[Sugestao]:
        """Extrai e converte sugestões do resultado do workflow."""
        sugestoes = []
        
        # Processa resultados de cada tarefa
        resultados_tarefas = resultado_workflow.get('resultados_por_tarefa', {})
        
        for tarefa_id, resultado_tarefa in resultados_tarefas.items():
            sugestoes_tarefa = self._converter_resultado_tarefa_para_sugestoes(
                tarefa_id, resultado_tarefa
            )
            sugestoes.extend(sugestoes_tarefa)
        
        # Remove duplicatas e ordena por prioridade
        sugestoes_unicas = self._remover_sugestoes_duplicadas(sugestoes)
        return sorted(sugestoes_unicas, key=lambda x: x.prioridade, reverse=True)
    
    def _converter_resultado_tarefa_para_sugestoes(
        self,
        tarefa_id: str,
        resultado_tarefa: Dict[str, Any]
    ) -> List[Sugestao]:
        """Converte resultado de uma tarefa específica em sugestões."""
        sugestoes = []
        
        if tarefa_id == "analise_performance":
            for problema in resultado_tarefa.get('problemas_encontrados', []):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.PERFORMANCE,
                    titulo=f"Otimização de {problema['tipo']}",
                    descricao=problema['descricao'],
                    impacto=problema['severidade'],
                    prioridade=self._mapear_severidade_para_prioridade(problema['severidade'])
                ))
        
        elif tarefa_id == "revisao_boas_praticas":
            for problema in resultado_tarefa.get('problemas_encontrados', []):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.BOAS_PRATICAS,
                    titulo=f"Melhoria em {problema['tipo']}",
                    descricao=problema['descricao'],
                    impacto=problema['severidade'],
                    prioridade=self._mapear_severidade_para_prioridade(problema['severidade'])
                ))
        
        elif tarefa_id == "auditoria_seguranca":
            for vuln in resultado_tarefa.get('vulnerabilidades_encontradas', []):
                sugestoes.append(Sugestao(
                    tipo=TipoSugestao.SEGURANCA,
                    titulo=f"Vulnerabilidade: {vuln.get('tipo', 'Desconhecida')}",
                    descricao=vuln.get('descricao', 'Vulnerabilidade de segurança identificada'),
                    impacto="alto",
                    prioridade=9
                ))
        
        return sugestoes
    
    def _mapear_severidade_para_prioridade(self, severidade: str) -> int:
        """Mapeia severidade para prioridade numérica."""
        mapeamento = {
            'baixa': 3,
            'media': 6,
            'alta': 9,
            'critica': 10
        }
        return mapeamento.get(severidade.lower(), 5)
    
    def _remover_sugestoes_duplicadas(self, sugestoes: List[Sugestao]) -> List[Sugestao]:
        """Remove sugestões duplicadas baseadas no título."""
        sugestoes_unicas = []
        titulos_vistos = set()
        
        for sugestao in sugestoes:
            if sugestao.titulo not in titulos_vistos:
                sugestoes_unicas.append(sugestao)
                titulos_vistos.add(sugestao.titulo)
        
        return sugestoes_unicas
    
    def _calcular_pontuacao_do_workflow(self, resultado_workflow: Dict[str, Any]) -> float:
        """Calcula pontuação de qualidade baseada no resultado do workflow."""
        
        # Extrai métricas finais se disponíveis
        metricas_finais = resultado_workflow.get('resultados_por_tarefa', {}).get(
            'consolidacao_resultados', {}
        ).get('metricas_finais', {})
        
        if metricas_finais:
            # Média ponderada das métricas
            score_qualidade = metricas_finais.get('score_qualidade', 80.0)
            score_performance = metricas_finais.get('score_performance', 80.0)
            score_seguranca = metricas_finais.get('score_seguranca', 90.0)
            
            # Pesos: qualidade 40%, performance 35%, segurança 25%
            pontuacao_final = (
                score_qualidade * 0.4 +
                score_performance * 0.35 +
                score_seguranca * 0.25
            )
            
            return round(pontuacao_final, 2)
        
        # Fallback para pontuação padrão
        return 75.0
    
    def _gerar_resumo_melhorias(self, sugestoes: List[Sugestao]) -> str:
        """Gera resumo das principais melhorias sugeridas."""
        if not sugestoes:
            return "Nenhuma melhoria específica identificada. Código em boa qualidade."
        
        # Agrupa sugestões por tipo
        tipos_count = {}
        for sugestao in sugestoes:
            tipo = sugestao.tipo.value
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        # Identifica principais áreas de melhoria
        principais_tipos = sorted(
            tipos_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        resumo_partes = []
        
        if principais_tipos:
            resumo_partes.append(f"Identificadas {len(sugestoes)} oportunidades de melhoria.")
            
            areas_principais = []
            for tipo, count in principais_tipos:
                tipo_nome = {
                    'performance': 'performance',
                    'legibilidade': 'legibilidade',
                    'boas_praticas': 'boas práticas',
                    'seguranca': 'segurança',
                    'manutencao': 'manutenção'
                }.get(tipo, tipo)
                
                areas_principais.append(f"{tipo_nome} ({count} sugestões)")
            
            resumo_partes.append(f"Principais áreas: {', '.join(areas_principais)}.")
        
        # Adiciona sugestão de prioridade alta se houver
        sugestoes_alta_prioridade = [s for s in sugestoes if s.prioridade >= 8]
        if sugestoes_alta_prioridade:
            resumo_partes.append(
                f"Recomenda-se priorizar {len(sugestoes_alta_prioridade)} "
                f"sugestões de alta prioridade."
            )
        
        return " ".join(resumo_partes)
    
    async def _executar_fallback_local(
        self,
        solicitacao: SolicitacaoAnalise
    ) -> RespostaAnalise:
        """Executa análise local como fallback em caso de erro no Crew AI."""
        logger.warning("Executando fallback para análise local")
        
        inicio_tempo = datetime.now()
        
        sugestoes = await self.analisador_local.analisar_codigo(
            codigo=solicitacao.codigo,
            nivel_detalhamento=solicitacao.nivel_detalhamento,
            focar_performance=solicitacao.focar_performance
        )
        
        tempo_analise = (datetime.now() - inicio_tempo).total_seconds()
        
        return RespostaAnalise(
            codigo_original=solicitacao.codigo,
            sugestoes=sugestoes,
            pontuacao_qualidade=self.analisador_local.calcular_pontuacao_qualidade(
                solicitacao.codigo
            ),
            tempo_analise=tempo_analise,
            timestamp=datetime.now(),
            resumo_melhorias="Análise realizada com agente local (modo fallback)."
        )
    
    def obter_status_workflows(self) -> Dict[str, Any]:
        """Obtém status de todos os workflows em execução."""
        return {
            'workflows_ativos': len([
                w for w in self.workflows_em_execucao.values()
                if w['status'] == 'executando'
            ]),
            'workflows_concluidos': len([
                w for w in self.workflows_em_execucao.values()
                if w['status'] == 'concluido'
            ]),
            'workflows_com_erro': len([
                w for w in self.workflows_em_execucao.values()
                if w['status'] == 'erro'
            ]),
            'detalhes': {
                wf_id: {
                    'status': wf_data['status'],
                    'inicio': wf_data['inicio'].isoformat(),
                    'nome_arquivo': wf_data['solicitacao'].nome_arquivo
                }
                for wf_id, wf_data in self.workflows_em_execucao.items()
            }
        }
    
    async def cancelar_workflow(self, workflow_id: str) -> bool:
        """
        Cancela um workflow em execução.
        
        Args:
            workflow_id: ID do workflow a ser cancelado
            
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        if workflow_id in self.workflows_em_execucao:
            self.workflows_em_execucao[workflow_id]['status'] = 'cancelado'
            logger.info(f"Workflow {workflow_id} cancelado")
            return True
        
        return False

