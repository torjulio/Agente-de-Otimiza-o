"""
Implementa a integração com o framework Crew AI para orquestração
de agentes e workflows de otimização de código.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict

from modelos.schemas import ConfiguracaoCrewAI, Sugestao, TipoSugestao

logger = logging.getLogger(__name__)

@dataclass
class TarefaWorkflow:
    """Representa uma tarefa no workflow do Crew AI."""
    id: str
    nome: str
    descricao: str
    agente_responsavel: str
    dependencias: List[str]
    status: str = "pendente"
    resultado: Optional[Dict[str, Any]] = None
    tempo_inicio: Optional[datetime] = None
    tempo_fim: Optional[datetime] = None

@dataclass
class AgenteCrewAI:
    """Representa um agente no sistema Crew AI."""
    id: str
    nome: str
    papel: str
    objetivo: str
    backstory: str
    habilidades: List[str]
    ferramentas: List[str]
    ativo: bool = True

class OrquestradorCrewAI:

    def __init__(self):
        self.configuracao = ConfiguracaoCrewAI()
        self.agentes_registrados = {}
        self.workflows_ativos = {}
        self.historico_execucoes = []
        self._inicializar_agentes_padrao()
    
    def _inicializar_agentes_padrao(self):
        """Inicializa os agentes padrão do sistema."""
        agentes_padrao = [
            AgenteCrewAI(
                id="otimizador_performance",
                nome="Especialista em Performance",
                papel="Analista de Performance de Código",
                objetivo="Identificar e sugerir otimizações de performance em código Python",
                backstory="Sou um especialista em otimização de código com 10 anos de experiência "
                         "em análise de performance e algoritmos eficientes.",
                habilidades=[
                    "analise_complexidade_algoritmica",
                    "otimizacao_loops",
                    "gerenciamento_memoria",
                    "profiling_codigo"
                ],
                ferramentas=[
                    "analisador_ast",
                    "profiler_memoria",
                    "medidor_tempo_execucao"
                ]
            ),
            AgenteCrewAI(
                id="revisor_boas_praticas",
                nome="Revisor de Boas Práticas",
                papel="Especialista em Qualidade de Código",
                objetivo="Garantir conformidade com boas práticas de programação Python",
                backstory="Sou um arquiteto de software especializado em qualidade de código "
                         "e padrões de desenvolvimento.",
                habilidades=[
                    "analise_pep8",
                    "padroes_design",
                    "clean_code",
                    "documentacao_codigo"
                ],
                ferramentas=[
                    "linter_python",
                    "analisador_docstrings",
                    "verificador_tipos"
                ]
            ),
            AgenteCrewAI(
                id="auditor_seguranca",
                nome="Auditor de Segurança",
                papel="Especialista em Segurança de Código",
                objetivo="Identificar vulnerabilidades e problemas de segurança no código",
                backstory="Sou um especialista em segurança cibernética focado em "
                         "análise estática de código e prevenção de vulnerabilidades.",
                habilidades=[
                    "analise_vulnerabilidades",
                    "seguranca_aplicacoes",
                    "auditoria_codigo",
                    "compliance_seguranca"
                ],
                ferramentas=[
                    "scanner_vulnerabilidades",
                    "analisador_sql_injection",
                    "verificador_xss"
                ]
            )
        ]
        
        for agente in agentes_padrao:
            self.agentes_registrados[agente.id] = agente
            logger.info(f"Agente registrado: {agente.nome}")
    
    async def criar_workflow_otimizacao(
        self,
        codigo: str,
        nome_arquivo: Optional[str] = None,
        prioridades: Optional[List[str]] = None
    ) -> str:
        """
        Cria um workflow de otimização de código.
        
        Args:
            codigo: Código Python a ser analisado
            nome_arquivo: Nome do arquivo (opcional)
            prioridades: Lista de prioridades para análise
            
        Returns:
            ID do workflow criado
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define as tarefas do workflow baseadas nas prioridades
        tarefas = self._definir_tarefas_workflow(codigo, prioridades or [])
        
        workflow = {
            'id': workflow_id,
            'nome': f"Otimização de {nome_arquivo or 'código anônimo'}",
            'codigo': codigo,
            'nome_arquivo': nome_arquivo,
            'tarefas': tarefas,
            'status': 'criado',
            'created_at': datetime.now(),
            'resultados': {}
        }
        
        self.workflows_ativos[workflow_id] = workflow
        logger.info(f"Workflow criado: {workflow_id} com {len(tarefas)} tarefas")
        
        return workflow_id
    
    def _definir_tarefas_workflow(
        self,
        codigo: str,
        prioridades: List[str]
    ) -> List[TarefaWorkflow]:
        """Define as tarefas do workflow baseadas no código e prioridades."""
        tarefas = []
        
        tarefas.append(TarefaWorkflow(
            id="analise_estrutura",
            nome="Análise de Estrutura do Código",
            descricao="Analisa a estrutura geral do código e identifica padrões",
            agente_responsavel="otimizador_performance",
            dependencias=[]
        ))
        
        if "performance" in prioridades or not prioridades:
            tarefas.append(TarefaWorkflow(
                id="analise_performance",
                nome="Análise de Performance",
                descricao="Identifica gargalos de performance e oportunidades de otimização",
                agente_responsavel="otimizador_performance",
                dependencias=["analise_estrutura"]
            ))
        
        # Tarefa 3: Revisão de boas práticas
        if "boas_praticas" in prioridades or not prioridades:
            tarefas.append(TarefaWorkflow(
                id="revisao_boas_praticas",
                nome="Revisão de Boas Práticas",
                descricao="Verifica conformidade com boas práticas de programação",
                agente_responsavel="revisor_boas_praticas",
                dependencias=["analise_estrutura"]
            ))
        
        # Tarefa 4: Auditoria de segurança
        if "seguranca" in prioridades or not prioridades:
            tarefas.append(TarefaWorkflow(
                id="auditoria_seguranca",
                nome="Auditoria de Segurança",
                descricao="Identifica vulnerabilidades e problemas de segurança",
                agente_responsavel="auditor_seguranca",
                dependencias=["analise_estrutura"]
            ))
        
        tarefas.append(TarefaWorkflow(
            id="consolidacao_resultados",
            nome="Consolidação de Resultados",
            descricao="Consolida todas as análises em um relatório final",
            agente_responsavel="otimizador_performance",
            dependencias=[t.id for t in tarefas if t.id != "consolidacao_resultados"]
        ))
        
        return tarefas
    
    async def executar_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Executa um workflow de otimização.
        
        Args:
            workflow_id: ID do workflow a ser executado
            
        Returns:
            Resultados da execução do workflow
        """
        if workflow_id not in self.workflows_ativos:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        workflow = self.workflows_ativos[workflow_id]
        workflow['status'] = 'executando'
        workflow['inicio_execucao'] = datetime.now()
        
        logger.info(f"Iniciando execução do workflow: {workflow_id}")
        
        try:
            # Executa as tarefas em ordem de dependência
            resultados_tarefas = {}
            
            for tarefa in workflow['tarefas']:
                if self._dependencias_concluidas(tarefa, resultados_tarefas):
                    resultado = await self._executar_tarefa(tarefa, workflow['codigo'])
                    resultados_tarefas[tarefa.id] = resultado
                    tarefa.status = "concluida"
                    tarefa.resultado = resultado
                    
                    logger.info(f"Tarefa concluída: {tarefa.nome}")
            
            # Consolida os resultados finais
            resultados_finais = self._consolidar_resultados(resultados_tarefas)
            
            workflow['status'] = 'concluido'
            workflow['fim_execucao'] = datetime.now()
            workflow['resultados'] = resultados_finais
            
            self.historico_execucoes.append({
                'workflow_id': workflow_id,
                'timestamp': datetime.now(),
                'duracao': (workflow['fim_execucao'] - workflow['inicio_execucao']).total_seconds(),
                'tarefas_executadas': len([t for t in workflow['tarefas'] if t.status == 'concluida']),
                'sucesso': True
            })
            
            logger.info(f"Workflow {workflow_id} concluído com sucesso!")
            return resultados_finais
            
        except Exception as e:
            workflow['status'] = 'erro'
            workflow['erro'] = str(e)
            logger.error(f"Erro na execução do workflow {workflow_id}: {e}")
            raise
    
    def _dependencias_concluidas(
        self,
        tarefa: TarefaWorkflow,
        resultados: Dict[str, Any]
    ) -> bool:
        """Verifica se todas as dependências de uma tarefa foram concluídas."""
        return all(dep in resultados for dep in tarefa.dependencias)
    
    async def _executar_tarefa(
        self,
        tarefa: TarefaWorkflow,
        codigo: str
    ) -> Dict[str, Any]:
        """
        Executa uma tarefa específica do workflow.
        
        Esta é uma simulação da execução real que seria feita pelo Crew AI.
        """
        tarefa.tempo_inicio = datetime.now()
        
        # Simula tempo de processamento
        await asyncio.sleep(0.1)
        
        agente = self.agentes_registrados.get(tarefa.agente_responsavel)
        if not agente:
            raise ValueError(f"Agente {tarefa.agente_responsavel} não encontrado")
        
        resultado = {}
        
        if tarefa.id == "analise_estrutura":
            resultado = self._simular_analise_estrutura(codigo)
        elif tarefa.id == "analise_performance":
            resultado = self._simular_analise_performance(codigo)
        elif tarefa.id == "revisao_boas_praticas":
            resultado = self._simular_revisao_boas_praticas(codigo)
        elif tarefa.id == "auditoria_seguranca":
            resultado = self._simular_auditoria_seguranca(codigo)
        elif tarefa.id == "consolidacao_resultados":
            resultado = self._simular_consolidacao_resultados(codigo)
        
        tarefa.tempo_fim = datetime.now()
        resultado['agente_executor'] = agente.nome
        resultado['tempo_execucao'] = (tarefa.tempo_fim - tarefa.tempo_inicio).total_seconds()
        
        return resultado
    
    def _simular_analise_estrutura(self, codigo: str) -> Dict[str, Any]:
        """Simula análise de estrutura do código."""
        linhas = codigo.split('\n')
        return {
            'tipo_analise': 'estrutura',
            'metricas': {
                'total_linhas': len(linhas),
                'linhas_codigo': len([l for l in linhas if l.strip() and not l.strip().startswith('#')]),
                'linhas_comentario': len([l for l in linhas if l.strip().startswith('#')]),
                'complexidade_estimada': min(10, len(linhas) // 10)
            },
            'padroes_identificados': [
                'funcoes_definidas',
                'classes_definidas',
                'imports_utilizados'
            ]
        }
    
    def _simular_analise_performance(self, codigo: str) -> Dict[str, Any]:
        """Simula análise de performance."""
        return {
            'tipo_analise': 'performance',
            'problemas_encontrados': [
                {
                    'tipo': 'loop_ineficiente',
                    'severidade': 'media',
                    'descricao': 'Loop com possível otimização usando list comprehension'
                },
                {
                    'tipo': 'concatenacao_strings',
                    'severidade': 'baixa',
                    'descricao': 'Concatenação de strings pode ser otimizada'
                }
            ],
            'sugestoes_otimizacao': [
                'Usar list comprehension em vez de loops simples',
                'Considerar uso de join() para concatenação de strings'
            ]
        }
    
    def _simular_revisao_boas_praticas(self, codigo: str) -> Dict[str, Any]:
        """Simula revisão de boas práticas."""
        return {
            'tipo_analise': 'boas_praticas',
            'conformidade_pep8': 85.0,
            'problemas_encontrados': [
                {
                    'tipo': 'nomenclatura',
                    'severidade': 'baixa',
                    'descricao': 'Algumas variáveis com nomes pouco descritivos'
                },
                {
                    'tipo': 'documentacao',
                    'severidade': 'media',
                    'descricao': 'Funções sem docstrings'
                }
            ],
            'recomendacoes': [
                'Adicionar docstrings às funções',
                'Usar nomes mais descritivos para variáveis'
            ]
        }
    
    def _simular_auditoria_seguranca(self, codigo: str) -> Dict[str, Any]:
        """Simula auditoria de segurança."""
        return {
            'tipo_analise': 'seguranca',
            'nivel_risco': 'baixo',
            'vulnerabilidades_encontradas': [],
            'recomendacoes_seguranca': [
                'Validar todas as entradas de usuário',
                'Usar parâmetros preparados em consultas SQL'
            ],
            'score_seguranca': 90.0
        }
    
    def _simular_consolidacao_resultados(self, codigo: str) -> Dict[str, Any]:
        """Simula consolidação de resultados."""
        return {
            'tipo_analise': 'consolidacao',
            'resumo_geral': {
                'qualidade_geral': 'boa',
                'principais_problemas': [
                    'Oportunidades de otimização de performance',
                    'Melhorias na documentação'
                ],
                'prioridades_implementacao': [
                    'Adicionar docstrings',
                    'Otimizar loops críticos'
                ]
            },
            'metricas_finais': {
                'score_qualidade': 82.0,
                'score_performance': 75.0,
                'score_seguranca': 90.0
            }
        }
    
    def _consolidar_resultados(self, resultados_tarefas: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida os resultados de todas as tarefas."""
        return {
            'workflow_completo': True,
            'timestamp': datetime.now().isoformat(),
            'resultados_por_tarefa': resultados_tarefas,
            'resumo_executivo': {
                'total_tarefas': len(resultados_tarefas),
                'tarefas_concluidas': len(resultados_tarefas),
                'tempo_total_execucao': sum(
                    r.get('tempo_execucao', 0) for r in resultados_tarefas.values()
                ),
                'agentes_utilizados': list(set(
                    r.get('agente_executor', '') for r in resultados_tarefas.values()
                ))
            }
        }
    
    def obter_status_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Obtém o status atual de um workflow."""
        if workflow_id not in self.workflows_ativos:
            return {'erro': 'Workflow não encontrado'}
        
        workflow = self.workflows_ativos[workflow_id]
        return {
            'id': workflow['id'],
            'nome': workflow['nome'],
            'status': workflow['status'],
            'progresso': self._calcular_progresso_workflow(workflow),
            'tarefas_concluidas': len([t for t in workflow['tarefas'] if t.status == 'concluida']),
            'total_tarefas': len(workflow['tarefas'])
        }
    
    def _calcular_progresso_workflow(self, workflow: Dict[str, Any]) -> float:
        """Calcula o progresso percentual de um workflow."""
        total_tarefas = len(workflow['tarefas'])
        tarefas_concluidas = len([t for t in workflow['tarefas'] if t.status == 'concluida'])
        return (tarefas_concluidas / total_tarefas) * 100 if total_tarefas > 0 else 0
    
    def listar_agentes_disponiveis(self) -> List[Dict[str, Any]]:
        """Lista todos os agentes disponíveis no sistema."""
        return [asdict(agente) for agente in self.agentes_registrados.values()]
    
    def obter_historico_execucoes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtém o histórico de execuções de workflows."""
        return sorted(
            self.historico_execucoes,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limite]
    
    def gerar_documentacao_integracao(self) -> str:
        """
        Gera documentação sobre como integrar com Crew AI real.
        
        Returns:
            Documentação em formato markdown
        """
        return """
# Integração com Crew AI - Documentação

## Visão Geral

Este documento descreve como integrar o Agente de Otimização de Código com o framework Crew AI
para orquestração avançada de agentes especializados.

## Configuração do Crew AI

### 1. Instalação
```bash
pip install crewai
```

### 2. Definição dos Agentes

```python
from crewai import Agent, Task, Crew

# Agente Otimizador de Performance
otimizador_performance = Agent(
    role='Especialista em Performance',
    goal='Identificar e sugerir otimizações de performance em código Python',
    backstory='Especialista com 10 anos de experiência em otimização de código',
    verbose=True,
    allow_delegation=False,
    tools=[analisador_ast, profiler_memoria]
)

# Agente Revisor de Boas Práticas
revisor_boas_praticas = Agent(
    role='Revisor de Qualidade',
    goal='Garantir conformidade com boas práticas de programação',
    backstory='Arquiteto de software especializado em qualidade de código',
    verbose=True,
    allow_delegation=False,
    tools=[linter_python, verificador_tipos]
)
```

### 3. Definição das Tarefas

```python
# Tarefa de análise de performance
tarefa_performance = Task(
    description='Analise o código fornecido e identifique oportunidades de otimização de performance',
    agent=otimizador_performance,
    expected_output='Lista detalhada de sugestões de otimização com exemplos de código'
)

# Tarefa de revisão de boas práticas
tarefa_boas_praticas = Task(
    description='Revise o código para conformidade com PEP 8 e boas práticas Python',
    agent=revisor_boas_praticas,
    expected_output='Relatório de conformidade com sugestões de melhoria'
)
```

### 4. Criação do Crew

```python
crew_otimizacao = Crew(
    agents=[otimizador_performance, revisor_boas_praticas],
    tasks=[tarefa_performance, tarefa_boas_praticas],
    verbose=2,
    process=Process.sequential
)
```

### 5. Execução

```python
resultado = crew_otimizacao.kickoff(inputs={'codigo': codigo_python})
```

## Integração com a API

### Endpoint para Crew AI

```python
@app.post("/crew-ai/analyze")
async def analisar_com_crew_ai(solicitacao: SolicitacaoAnalise):
    # Inicializa o crew
    crew = inicializar_crew_otimizacao()
    
    # Executa a análise
    resultado = crew.kickoff(inputs={
        'codigo': solicitacao.codigo,
        'nome_arquivo': solicitacao.nome_arquivo
    })
    
    # Processa e retorna os resultados
    return processar_resultado_crew(resultado)
```

## Configurações Avançadas

### Ferramentas Personalizadas

```python
from crewai_tools import BaseTool

class AnalisadorASTTool(BaseTool):
    name: str = "Analisador AST"
    description: str = "Analisa a árvore sintática abstrata do código Python"
    
    def _run(self, codigo: str) -> str:
        # Implementação da análise AST
        return resultado_analise
```

### Callbacks e Monitoramento

```python
def callback_progresso(step_output):
    logger.info(f"Passo concluído: {step_output}")

crew_otimizacao = Crew(
    agents=[...],
    tasks=[...],
    step_callback=callback_progresso
)
```

## Benefícios da Integração

1. **Especialização**: Cada agente foca em um aspecto específico da análise
2. **Paralelização**: Tarefas independentes podem ser executadas em paralelo
3. **Flexibilidade**: Fácil adição de novos agentes e tarefas
4. **Rastreabilidade**: Histórico completo de execução e decisões
5. **Escalabilidade**: Distribuição de carga entre múltiplos agentes

## Considerações de Performance

- Use cache para análises repetitivas
- Implemente timeouts para tarefas longas
- Configure pools de agentes para alta demanda
- Monitore uso de recursos e ajuste conforme necessário

## Próximos Passos

1. Implementar ferramentas personalizadas específicas para análise de código
2. Configurar agentes especializados por linguagem/framework
3. Integrar com sistemas de CI/CD para análise automática
4. Desenvolver dashboard para monitoramento de workflows
"""

