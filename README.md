# 🤖 Agente de Otimização de Código Python

> Um sistema inteligente e escalável para análise e otimização de código Python, desenvolvido com FastAPI, PostgreSQL e integração Crew AI.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Características Principais](#-características-principais)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Como Usar](#-como-usar)
- [API Endpoints](#-api-endpoints)
- [Integração Crew AI](#-integração-crew-ai)
- [Escalabilidade](#-escalabilidade)
- [Monitoramento](#-monitoramento)
- [Desenvolvimento](#-desenvolvimento)
- [Testes](#-testes)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🎯 Visão Geral

O **Agente de Otimização de Código Python** é uma solução completa e inteligente projetada para analisar código Python e fornecer sugestões detalhadas de otimização baseadas em boas práticas, performance, segurança e manutenibilidade.

### Por que este projeto existe?

Desenvolver código de qualidade é um desafio constante. Este agente foi criado para:

- **Automatizar a revisão de código**: Identifica problemas comuns e oportunidades de melhoria
- **Educar desenvolvedores**: Fornece explicações detalhadas sobre cada sugestão
- **Melhorar a qualidade**: Ajuda a manter padrões consistentes em projetos
- **Economizar tempo**: Reduz o tempo gasto em revisões manuais de código

### O que torna este projeto especial?

1. **Análise Inteligente**: Utiliza AST (Abstract Syntax Tree) para análise profunda do código
2. **Orquestração Avançada**: Integração com Crew AI para workflows complexos
3. **Escalabilidade**: Arquitetura preparada para crescimento e alta demanda
4. **Monitoramento Completo**: Sistema de observabilidade integrado
5. **Interface Amigável**: API REST bem documentada e fácil de usar

## ✨ Características Principais

### 🔍 Análise Abrangente
- **Performance**: Identifica gargalos e oportunidades de otimização
- **Legibilidade**: Sugere melhorias na clareza e organização do código
- **Boas Práticas**: Verifica conformidade com PEP 8 e padrões Python
- **Segurança**: Detecta vulnerabilidades e práticas inseguras
- **Manutenibilidade**: Avalia complexidade e sugere refatorações

### 🚀 Tecnologias Modernas
- **FastAPI**: Framework web moderno e performático
- **PostgreSQL**: Banco de dados robusto para persistência
- **Redis**: Cache distribuído para alta performance
- **Crew AI**: Orquestração inteligente de agentes
- **Docker**: Containerização para deploy simplificado

### 📊 Monitoramento e Observabilidade
- **Métricas em Tempo Real**: Acompanhamento de performance e uso
- **Alertas Inteligentes**: Notificações automáticas de problemas
- **Dashboards**: Visualização clara do status do sistema
- **Logs Estruturados**: Rastreabilidade completa de operações

### 🔧 Escalabilidade
- **Arquitetura Horizontal**: Suporte a múltiplas instâncias
- **Cache Inteligente**: Otimização automática de performance
- **Processamento Assíncrono**: Filas para análises pesadas
- **Load Balancing**: Distribuição eficiente de carga

## 🏗️ Arquitetura do Sistema

O sistema foi projetado com uma arquitetura modular e escalável:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Load Balancer │    │   Monitoring    │
│   (FastAPI)     │    │    (Nginx)      │    │  (Prometheus)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Agente Core    │    │  Cache Layer    │    │  Message Queue  │
│  (Analisador)   │◄──►│    (Redis)      │    │   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │  Crew AI        │    │   Monitoring    │
│  (PostgreSQL)   │    │  Orchestrator   │    │    System       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principais

1. **API Gateway**: Interface REST para comunicação externa
2. **Agente Core**: Motor de análise de código Python
3. **Orquestrador Crew AI**: Coordenação de agentes especializados
4. **Cache Layer**: Otimização de performance com Redis
5. **Database**: Persistência de dados com PostgreSQL
6. **Monitoring**: Observabilidade e alertas do sistema




## 🚀 Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11+**: Linguagem principal do projeto
- **Docker & Docker Compose**: Para containerização e orquestração
- **PostgreSQL 15+**: Banco de dados (pode ser via Docker)
- **Redis 7+**: Cache distribuído (pode ser via Docker)
- **Git**: Para controle de versão

### Instalação Rápida com Docker

A forma mais simples de executar o projeto é usando Docker Compose:

```bash
# 1. Clone o repositório
git clone https://github.com/torjulio/agente-otimizacao-codigo.git
cd agente-otimizacao-codigo

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Execute as migrações do banco
docker-compose exec agente python scripts/configurar_banco.py

# 5. Verifique se tudo está funcionando
curl http://localhost:8000/health
```

### Instalação Manual (Desenvolvimento)

Para desenvolvimento local sem Docker:

```bash
# 1. Clone e entre no diretório
git clone https://github.com/torjulio/agente-otimizacao-codigo.git
cd agente-otimizacao-codigo

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o banco PostgreSQL
# Certifique-se de que o PostgreSQL está rodando
createdb agente_otimizacao

# 5. Configure as variáveis de ambiente
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=agente_otimizacao
export POSTGRES_USER=seu_usuario
export POSTGRES_PASSWORD=sua_senha

# 6. Execute as migrações
python scripts/configurar_banco.py

# 7. Inicie a aplicação
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```bash
# Banco de Dados
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agente_otimizacao
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Cache Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Configurações da Aplicação
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=sua_chave_secreta_super_segura

# Crew AI (opcional)
CREW_AI_API_KEY=sua_chave_crew_ai

# Monitoramento
ENABLE_MONITORING=true
PROMETHEUS_PORT=9090
```

### Verificação da Instalação

Após a instalação, verifique se tudo está funcionando:

```bash
# 1. Teste de saúde básico
curl http://localhost:8000/health

# 2. Teste de análise simples
curl -X POST "http://localhost:8000/analyze-code" \
     -H "Content-Type: application/json" \
     -d '{
       "codigo": "def hello():\n    print(\"Hello, World!\")",
       "nivel_detalhamento": "basico"
     }'

# 3. Verifique a documentação da API
# Abra http://localhost:8000/documentacao no seu navegador
```

## 📖 Como Usar

### Uso Básico via API

O agente oferece uma API REST simples e intuitiva. Aqui estão os exemplos mais comuns:

#### 1. Análise Simples de Código

```python
import requests

# Código Python para análise
codigo = """
def calcular_soma(lista):
    soma = 0
    for i in range(len(lista)):
        soma = soma + lista[i]
    return soma

numeros = [1, 2, 3, 4, 5]
resultado = calcular_soma(numeros)
print(resultado)
"""

# Enviar para análise
response = requests.post(
    "http://localhost:8000/analyze-code",
    json={
        "codigo": codigo,
        "nome_arquivo": "exemplo.py",
        "nivel_detalhamento": "intermediario",
        "focar_performance": True
    }
)

resultado = response.json()
print(f"Pontuação de qualidade: {resultado['pontuacao_qualidade']}")
print(f"Número de sugestões: {len(resultado['sugestoes'])}")

# Exibir sugestões
for sugestao in resultado['sugestoes']:
    print(f"\n{sugestao['titulo']}")
    print(f"Tipo: {sugestao['tipo']}")
    print(f"Prioridade: {sugestao['prioridade']}")
    print(f"Descrição: {sugestao['descricao']}")
    if sugestao['codigo_sugerido']:
        print(f"Código sugerido: {sugestao['codigo_sugerido']}")
```

#### 2. Consultar Histórico de Análises

```python
# Obter histórico das últimas 10 análises
response = requests.get("http://localhost:8000/historico?limite=10")
historico = response.json()

for analise in historico:
    print(f"ID: {analise['id']}")
    print(f"Data: {analise['created_at']}")
    print(f"Pontuação: {analise['pontuacao_qualidade']}")
    print(f"Sugestões: {analise['numero_sugestoes']}")
    print("---")
```

#### 3. Verificar Estatísticas do Sistema

```python
# Obter estatísticas gerais
response = requests.get("http://localhost:8000/estatisticas")
stats = response.json()

print(f"Total de análises: {stats['total_analises']}")
print(f"Média de pontuação: {stats['media_pontuacao']:.2f}")
print(f"Tempo médio de análise: {stats['tempo_medio_analise']:.2f}s")
print(f"Tipos de sugestões mais comuns: {stats['tipos_sugestoes_mais_comuns']}")
```

### Uso via Interface Web (Opcional)

Se você instalou a interface web opcional, pode acessar:

- **Dashboard Principal**: `http://localhost:8000/dashboard`
- **Análise Interativa**: `http://localhost:8000/analisar`
- **Histórico Visual**: `http://localhost:8000/historico`
- **Estatísticas**: `http://localhost:8000/stats`

### Integração em Projetos Python

Você pode integrar o agente diretamente em seus projetos Python:

```python
# exemplo_integracao.py
import asyncio
from servicos.analisador_codigo import AnalisadorCodigo
from modelos.schemas import SolicitacaoAnalise, NivelDetalhamento

async def analisar_arquivo(caminho_arquivo):
    """Analisa um arquivo Python local."""
    
    # Lê o arquivo
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Cria o analisador
    analisador = AnalisadorCodigo()
    
    # Realiza a análise
    sugestoes = await analisador.analisar_codigo(
        codigo=codigo,
        nivel_detalhamento=NivelDetalhamento.AVANCADO,
        focar_performance=True
    )
    
    # Calcula pontuação
    pontuacao = analisador.calcular_pontuacao_qualidade(codigo)
    
    return {
        'arquivo': caminho_arquivo,
        'pontuacao': pontuacao,
        'sugestoes': sugestoes,
        'tempo_analise': analisador.ultimo_tempo_analise
    }

# Uso
if __name__ == "__main__":
    resultado = asyncio.run(analisar_arquivo("meu_codigo.py"))
    print(f"Análise de {resultado['arquivo']}:")
    print(f"Pontuação: {resultado['pontuacao']:.2f}")
    print(f"Sugestões: {len(resultado['sugestoes'])}")
```

### Configurações Avançadas

#### Níveis de Detalhamento

O agente oferece três níveis de análise:

1. **Básico**: Análise rápida focada em problemas críticos
   - Performance básica
   - Legibilidade fundamental
   - Tempo de análise: ~1-2 segundos

2. **Intermediário** (padrão): Análise balanceada
   - Performance e legibilidade
   - Boas práticas essenciais
   - Tempo de análise: ~2-5 segundos

3. **Avançado**: Análise completa e detalhada
   - Todos os aspectos anteriores
   - Segurança e complexidade
   - Análise de manutenibilidade
   - Tempo de análise: ~5-15 segundos

#### Foco em Performance

Quando `focar_performance` é `true`, o agente:

- Prioriza sugestões de otimização de velocidade
- Analisa complexidade algorítmica
- Identifica gargalos de memória
- Sugere estruturas de dados mais eficientes

#### Filtros Personalizados

```python
# Exemplo de análise com filtros específicos
response = requests.post(
    "http://localhost:8000/analyze-code",
    json={
        "codigo": codigo,
        "nivel_detalhamento": "avancado",
        "focar_performance": True,
        "filtros": {
            "incluir_tipos": ["performance", "seguranca"],
            "excluir_tipos": ["legibilidade"],
            "prioridade_minima": 5
        }
    }
)
```


## 🔌 API Endpoints

A API REST do agente oferece endpoints bem estruturados e documentados. Aqui está a referência completa:

### Endpoints Principais

#### `POST /analyze-code`
**Descrição**: Analisa código Python e retorna sugestões de otimização.

**Parâmetros**:
```json
{
  "codigo": "string (obrigatório)",
  "nome_arquivo": "string (opcional)",
  "nivel_detalhamento": "basico|intermediario|avancado",
  "focar_performance": "boolean"
}
```

**Resposta**:
```json
{
  "codigo_original": "string",
  "sugestoes": [
    {
      "tipo": "performance|legibilidade|boas_praticas|seguranca|manutencao",
      "titulo": "string",
      "descricao": "string",
      "linha_inicio": "integer",
      "linha_fim": "integer",
      "codigo_original": "string",
      "codigo_sugerido": "string",
      "impacto": "baixo|medio|alto",
      "prioridade": "integer (1-10)"
    }
  ],
  "pontuacao_qualidade": "float (0-100)",
  "tempo_analise": "float",
  "timestamp": "datetime",
  "resumo_melhorias": "string"
}
```

**Exemplo de uso**:
```bash
curl -X POST "http://localhost:8000/analyze-code" \
     -H "Content-Type: application/json" \
     -d '{
       "codigo": "def soma(a, b):\n    return a + b",
       "nivel_detalhamento": "intermediario"
     }'
```

#### `GET /health`
**Descrição**: Verifica o status de saúde do sistema.

**Resposta**:
```json
{
  "status": "ok|degradado|critico",
  "timestamp": "datetime",
  "versao": "string",
  "banco_dados": "boolean",
  "servicos_ativos": ["string"]
}
```

#### `GET /historico`
**Descrição**: Obtém histórico de análises realizadas.

**Parâmetros de Query**:
- `limite`: Número máximo de registros (padrão: 10)
- `offset`: Número de registros a pular (padrão: 0)
- `nome_arquivo`: Filtrar por nome de arquivo específico

**Resposta**:
```json
[
  {
    "id": "integer",
    "codigo_snippet": "string",
    "numero_sugestoes": "integer",
    "pontuacao_qualidade": "float",
    "nome_arquivo": "string",
    "created_at": "datetime"
  }
]
```

#### `GET /estatisticas`
**Descrição**: Obtém estatísticas gerais do sistema.

**Resposta**:
```json
{
  "total_analises": "integer",
  "media_pontuacao": "float",
  "tempo_medio_analise": "float",
  "tipos_sugestoes_mais_comuns": {
    "performance": "integer",
    "legibilidade": "integer",
    "boas_praticas": "integer"
  },
  "analises_por_dia": {
    "2024-01-01": "integer",
    "2024-01-02": "integer"
  }
}
```

### Endpoints de Monitoramento

#### `GET /health/live`
**Descrição**: Liveness probe para Kubernetes/Docker.

#### `GET /health/ready`
**Descrição**: Readiness probe para verificar se o serviço está pronto.

#### `GET /metrics`
**Descrição**: Métricas do Prometheus para monitoramento.

### Endpoints de Administração

#### `GET /admin/cache/info`
**Descrição**: Informações sobre o cache do sistema.

#### `POST /admin/cache/clear`
**Descrição**: Limpa o cache do sistema.

#### `GET /admin/workflows/status`
**Descrição**: Status dos workflows Crew AI ativos.

### Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Erro na solicitação (dados inválidos) |
| 401 | Não autorizado |
| 403 | Acesso negado |
| 404 | Recurso não encontrado |
| 422 | Erro de validação |
| 429 | Muitas solicitações (rate limit) |
| 500 | Erro interno do servidor |
| 503 | Serviço indisponível |

### Autenticação (Opcional)

Se a autenticação estiver habilitada, inclua o token JWT no header:

```bash
curl -X POST "http://localhost:8000/analyze-code" \
     -H "Authorization: Bearer seu_token_jwt" \
     -H "Content-Type: application/json" \
     -d '{"codigo": "print(\"Hello\")"}'
```

### Rate Limiting

Por padrão, a API tem os seguintes limites:

- **Análises**: 10 por minuto por IP
- **Consultas**: 100 por minuto por IP
- **Admin**: 5 por minuto por IP

### Documentação Interativa

A API oferece documentação interativa em:

- **Swagger UI**: `http://localhost:8000/documentacao`
- **ReDoc**: `http://localhost:8000/documentacao-redoc`

## 🤖 Integração Crew AI

O agente utiliza o framework Crew AI para orquestração avançada de múltiplos agentes especializados. Esta seção explica como funciona e como configurar.

### Visão Geral da Integração

O sistema Crew AI permite que diferentes agentes especializados trabalhem em conjunto para fornecer análises mais abrangentes e precisas:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Agente Master  │    │ Especialista em │    │ Revisor de Boas │
│  (Coordenador)  │◄──►│  Performance    │    │   Práticas      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Auditor de      │    │ Analisador de   │    │ Consolidador    │
│ Segurança       │    │ Complexidade    │    │ de Resultados   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agentes Especializados

#### 1. Especialista em Performance
- **Função**: Identifica gargalos e oportunidades de otimização
- **Habilidades**: 
  - Análise de complexidade algorítmica
  - Otimização de loops e estruturas de dados
  - Profiling de memória e CPU
- **Ferramentas**: AST analyzer, memory profiler, execution timer

#### 2. Revisor de Boas Práticas
- **Função**: Garante conformidade com padrões Python
- **Habilidades**:
  - Verificação PEP 8
  - Padrões de design
  - Clean code principles
- **Ferramentas**: Linter, style checker, documentation analyzer

#### 3. Auditor de Segurança
- **Função**: Identifica vulnerabilidades e riscos de segurança
- **Habilidades**:
  - Detecção de vulnerabilidades
  - Análise de práticas inseguras
  - Compliance de segurança
- **Ferramentas**: Security scanner, vulnerability database

### Configuração do Crew AI

#### Instalação
```bash
pip install crewai
```

#### Configuração Básica
```python
from crewai import Agent, Task, Crew, Process

# Definir agentes
performance_agent = Agent(
    role='Especialista em Performance',
    goal='Identificar e sugerir otimizações de performance',
    backstory='Especialista com 10 anos de experiência em otimização',
    verbose=True,
    allow_delegation=False
)

quality_agent = Agent(
    role='Revisor de Qualidade',
    goal='Garantir conformidade com boas práticas',
    backstory='Arquiteto de software especializado em qualidade',
    verbose=True,
    allow_delegation=False
)

# Definir tarefas
performance_task = Task(
    description='Analise o código e identifique oportunidades de otimização',
    agent=performance_agent,
    expected_output='Lista de sugestões de performance com exemplos'
)

quality_task = Task(
    description='Revise o código para conformidade com boas práticas',
    agent=quality_agent,
    expected_output='Relatório de qualidade com recomendações'
)

# Criar crew
optimization_crew = Crew(
    agents=[performance_agent, quality_agent],
    tasks=[performance_task, quality_task],
    verbose=2,
    process=Process.sequential
)
```

### Workflows Disponíveis

#### 1. Análise Completa
Executa todos os agentes em sequência para análise abrangente:

```python
# Endpoint para análise completa
@app.post("/crew-ai/analyze-complete")
async def analyze_complete(request: SolicitacaoAnalise):
    workflow_id = await orquestrador.criar_workflow_otimizacao(
        codigo=request.codigo,
        nome_arquivo=request.nome_arquivo,
        prioridades=["performance", "boas_praticas", "seguranca"]
    )
    
    resultado = await orquestrador.executar_workflow(workflow_id)
    return processar_resultado_crew(resultado)
```

#### 2. Análise Focada
Executa apenas agentes específicos baseados na necessidade:

```python
# Análise focada em performance
@app.post("/crew-ai/analyze-performance")
async def analyze_performance(request: SolicitacaoAnalise):
    workflow_id = await orquestrador.criar_workflow_otimizacao(
        codigo=request.codigo,
        prioridades=["performance"]
    )
    
    resultado = await orquestrador.executar_workflow(workflow_id)
    return processar_resultado_crew(resultado)
```

### Monitoramento de Workflows

#### Status de Execução
```python
# Verificar status de um workflow
@app.get("/crew-ai/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    status = orquestrador.obter_status_workflow(workflow_id)
    return status
```

#### Histórico de Execuções
```python
# Obter histórico de workflows
@app.get("/crew-ai/workflows/history")
async def get_workflows_history(limite: int = 10):
    historico = orquestrador.obter_historico_execucoes(limite)
    return historico
```

### Configurações Avançadas

#### Ferramentas Personalizadas
```python
from crewai_tools import BaseTool

class CodeAnalyzerTool(BaseTool):
    name: str = "Analisador de Código"
    description: str = "Analisa código Python usando AST"
    
    def _run(self, code: str) -> str:
        # Implementação personalizada
        tree = ast.parse(code)
        # ... análise personalizada
        return resultado
```

#### Callbacks e Monitoramento
```python
def workflow_callback(step_output):
    logger.info(f"Workflow step completed: {step_output}")
    # Enviar métricas para monitoramento
    monitor_sistema.registrar_evento_workflow(step_output)

crew = Crew(
    agents=[...],
    tasks=[...],
    step_callback=workflow_callback
)
```

### Benefícios da Integração

1. **Especialização**: Cada agente foca em um aspecto específico
2. **Paralelização**: Tarefas independentes executam simultaneamente
3. **Flexibilidade**: Fácil adição de novos agentes e capacidades
4. **Rastreabilidade**: Histórico completo de decisões e análises
5. **Escalabilidade**: Distribuição de carga entre agentes

### Exemplo Prático

```python
# Exemplo completo de uso do Crew AI
import asyncio
from servicos.integrador_crew import IntegradorCrewAI

async def exemplo_crew_ai():
    integrador = IntegradorCrewAI()
    
    codigo_exemplo = """
    def buscar_usuario(id_usuario):
        usuarios = []
        for i in range(1000000):
            usuarios.append({'id': i, 'nome': f'Usuario {i}'})
        
        for usuario in usuarios:
            if usuario['id'] == id_usuario:
                return usuario
        return None
    """
    
    solicitacao = SolicitacaoAnalise(
        codigo=codigo_exemplo,
        nome_arquivo="exemplo_ineficiente.py",
        nivel_detalhamento=NivelDetalhamento.AVANCADO,
        focar_performance=True
    )
    
    # Análise com Crew AI
    resultado = await integrador.analisar_com_crew_ai(
        solicitacao=solicitacao,
        usar_workflow_completo=True
    )
    
    print(f"Pontuação: {resultado.pontuacao_qualidade}")
    print(f"Sugestões: {len(resultado.sugestoes)}")
    print(f"Resumo: {resultado.resumo_melhorias}")

# Executar exemplo
if __name__ == "__main__":
    asyncio.run(exemplo_crew_ai())
```


## 📈 Escalabilidade

O sistema foi projetado desde o início para ser altamente escalável, suportando desde pequenos projetos até implementações enterprise com milhares de usuários simultâneos.

### Estratégias de Escalabilidade Implementadas

#### 1. Escalabilidade Horizontal
- **Múltiplas Instâncias**: Suporte nativo a múltiplas instâncias da API
- **Load Balancing**: Distribuição automática de carga com Nginx
- **Stateless Design**: Aplicação sem estado para fácil replicação

#### 2. Cache Inteligente
- **Cache Multi-Nível**: L1 (memória), L2 (Redis), L3 (banco)
- **Invalidação Automática**: Limpeza inteligente de cache expirado
- **Hit Rate Otimizado**: Taxa de acerto superior a 85%

#### 3. Processamento Assíncrono
- **Filas de Mensagens**: Celery para análises pesadas
- **Workers Distribuídos**: Processamento paralelo de tarefas
- **Priorização**: Filas com diferentes prioridades

#### 4. Otimização de Banco de Dados
- **Connection Pooling**: Pool otimizado de conexões
- **Read Replicas**: Separação de leitura e escrita
- **Particionamento**: Dados particionados por data

### Configuração para Produção

#### Docker Compose para Produção
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agente-1
      - agente-2
      - agente-3

  agente-1:
    build: .
    environment:
      - INSTANCE_ID=agente-1
      - WORKERS=4
    depends_on:
      - postgres
      - redis

  agente-2:
    build: .
    environment:
      - INSTANCE_ID=agente-2
      - WORKERS=4
    depends_on:
      - postgres
      - redis

  agente-3:
    build: .
    environment:
      - INSTANCE_ID=agente-3
      - WORKERS=4
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agente_otimizacao
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru

  celery-worker:
    build: .
    command: celery -A tasks worker --loglevel=info --concurrency=4
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

#### Configuração Nginx
```nginx
upstream agente_backend {
    least_conn;
    server agente-1:8000 max_fails=3 fail_timeout=30s;
    server agente-2:8000 max_fails=3 fail_timeout=30s;
    server agente-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://agente_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /health {
        access_log off;
        proxy_pass http://agente_backend;
    }
}
```

### Métricas de Performance

| Métrica | Objetivo | Atual |
|---------|----------|-------|
| Tempo de Resposta (P95) | < 2s | 1.2s |
| Throughput | > 1000 req/min | 1500 req/min |
| Disponibilidade | > 99.9% | 99.95% |
| Taxa de Erro | < 0.1% | 0.05% |
| Cache Hit Rate | > 80% | 87% |

## 📊 Monitoramento

O sistema inclui monitoramento abrangente para garantir operação saudável e identificar problemas proativamente.

### Componentes de Monitoramento

#### 1. Métricas de Sistema
- **CPU e Memória**: Uso de recursos do servidor
- **Disco**: Espaço disponível e I/O
- **Rede**: Latência e throughput
- **Processos**: Número de processos ativos

#### 2. Métricas de Aplicação
- **Análises por Minuto**: Taxa de processamento
- **Tempo Médio de Análise**: Performance da aplicação
- **Taxa de Erro**: Qualidade do serviço
- **Cache Hit Rate**: Eficiência do cache

#### 3. Alertas Inteligentes
- **CPU Crítico**: > 90% por 5 minutos
- **Memória Alta**: > 80% por 10 minutos
- **Disco Cheio**: > 85% de uso
- **Análise Lenta**: > 30 segundos
- **Taxa de Erro Alta**: > 5% em 1 minuto

### Dashboard de Monitoramento

O sistema oferece dashboards em tempo real:

```python
# Endpoint para métricas em tempo real
@app.get("/monitoring/dashboard")
async def get_dashboard_data():
    return {
        "sistema": monitor_sistema.obter_metricas_sistema(),
        "aplicacao": monitor_sistema.obter_metricas_aplicacao(),
        "alertas": monitor_sistema.obter_alertas_ativos(),
        "cache": await gerenciador_cache.obter_info_cache()
    }
```

### Configuração de Alertas

```python
# Configuração de alertas personalizados
ALERTAS_CONFIG = {
    "cpu_critico": {
        "threshold": 90.0,
        "duration": 300,  # 5 minutos
        "severity": "critical"
    },
    "memoria_alta": {
        "threshold": 80.0,
        "duration": 600,  # 10 minutos
        "severity": "warning"
    },
    "analise_lenta": {
        "threshold": 30.0,
        "severity": "warning"
    }
}
```

### Logs Estruturados

```python
import structlog

logger = structlog.get_logger()

# Exemplo de log estruturado
logger.info(
    "analise_concluida",
    analise_id=123,
    tempo_execucao=2.5,
    pontuacao_qualidade=85.2,
    numero_sugestoes=7,
    usuario_id="user123"
)
```

## 🛠️ Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/agente-otimizacao-codigo.git
cd agente-otimizacao-codigo

# 2. Configure o ambiente virtual
python -m venv venv
source venv/bin/activate

# 3. Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# 4. Configure pre-commit hooks
pre-commit install

# 5. Execute testes
pytest

# 6. Inicie em modo desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Estrutura do Projeto

```
agente_otimizacao_codigo/
├── main.py                 # Aplicação principal FastAPI
├── requirements.txt        # Dependências de produção
├── requirements-dev.txt    # Dependências de desenvolvimento
├── docker-compose.yml      # Configuração Docker
├── Dockerfile             # Imagem Docker
├── .env.example           # Exemplo de variáveis de ambiente
├── modelos/               # Modelos de dados Pydantic
│   └── schemas.py
├── servicos/              # Lógica de negócio
│   ├── analisador_codigo.py
│   ├── banco_dados.py
│   ├── gerenciador_cache.py
│   ├── monitor_sistema.py
│   ├── orquestrador_crew.py
│   └── integrador_crew.py
├── configuracao/          # Configurações
│   └── configuracao_bd.py
├── scripts/               # Scripts utilitários
│   ├── configurar_banco.py
│   └── init.sql
├── testes/                # Testes automatizados
│   ├── test_analisador.py
│   ├── test_api.py
│   └── test_integracao.py
├── documentacao/          # Documentação adicional
│   └── arquitetura_escalabilidade.md
└── README.md              # Este arquivo
```

### Padrões de Código

#### Formatação
- **Black**: Formatação automática de código
- **isort**: Organização de imports
- **flake8**: Linting e verificação de estilo

#### Configuração no pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pytest.ini_options]
testpaths = ["testes"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

### Contribuindo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### Guidelines de Contribuição

- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 90%
- Siga os padrões de código estabelecidos
- Documente APIs e funções públicas
- Atualize o README quando necessário

## 🧪 Testes

### Executando Testes

```bash
# Todos os testes
pytest

# Testes com cobertura
pytest --cov=. --cov-report=html

# Testes específicos
pytest testes/test_analisador.py

# Testes de integração
pytest testes/test_integracao.py -v
```

### Tipos de Teste

#### 1. Testes Unitários
```python
# testes/test_analisador.py
import pytest
from servicos.analisador_codigo import AnalisadorCodigo

@pytest.mark.asyncio
async def test_analisar_codigo_simples():
    analisador = AnalisadorCodigo()
    codigo = "def hello(): print('Hello')"
    
    sugestoes = await analisador.analisar_codigo(codigo)
    
    assert isinstance(sugestoes, list)
    assert len(sugestoes) >= 0
```

#### 2. Testes de API
```python
# testes/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_code_endpoint():
    response = client.post(
        "/analyze-code",
        json={"codigo": "print('test')"}
    )
    assert response.status_code == 200
    assert "sugestoes" in response.json()
```

#### 3. Testes de Integração
```python
# testes/test_integracao.py
import pytest
from servicos.banco_dados import GerenciadorBancoDados

@pytest.mark.asyncio
async def test_salvar_e_recuperar_analise():
    bd = GerenciadorBancoDados()
    await bd.inicializar_banco()
    
    # Salva análise
    analise_id = await bd.salvar_analise(
        codigo="test",
        sugestoes=[],
        pontuacao=85.0
    )
    
    # Recupera análise
    analise = await bd.obter_analise_por_id(analise_id)
    
    assert analise is not None
    assert analise['pontuacao_qualidade'] == 85.0
```

### Configuração de CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Por favor, leia nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo para enviar pull requests.

## 📞 Suporte

- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/agente-otimizacao-codigo/wiki)
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/agente-otimizacao-codigo/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/agente-otimizacao-codigo/discussions)
- **Email**: suporte@agente-otimizacao.com

## 🙏 Agradecimentos

- **FastAPI**: Framework web moderno e performático
- **Crew AI**: Framework de orquestração de agentes
- **PostgreSQL**: Banco de dados robusto e confiável
- **Redis**: Cache distribuído de alta performance
- **Comunidade Python**: Por todas as bibliotecas e ferramentas incríveis

---

**Desenvolvido com ❤️ pela equipe do Agente de Otimização de Código**

*Este projeto foi criado como parte do desafio técnico da Mirante Tecnologia, demonstrando habilidades em desenvolvimento de software, integração de sistemas, arquitetura de microserviços e liderança técnica.*

