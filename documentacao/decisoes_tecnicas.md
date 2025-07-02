# 🏗️ Decisões Técnicas - Agente de Otimização de Código

## Introdução

Este documento detalha as principais decisões técnicas tomadas durante o desenvolvimento do Agente de Otimização de Código Python, explicando o raciocínio por trás de cada escolha e as alternativas consideradas.

## 🎯 Filosofia de Design

### Princípios Fundamentais

1. **Simplicidade**: A API deve ser intuitiva e fácil de usar
2. **Escalabilidade**: O sistema deve crescer com a demanda
3. **Observabilidade**: Tudo deve ser monitorável e rastreável
4. **Modularidade**: Componentes independentes e reutilizáveis
5. **Performance**: Resposta rápida mesmo com código complexo

### Abordagem de Desenvolvimento

Optamos por uma abordagem **API-first** onde:
- A API REST é o ponto central do sistema
- Interfaces podem ser construídas sobre a API
- Integração com outros sistemas é facilitada
- Testabilidade é maximizada

## 🛠️ Escolhas de Tecnologia

### Framework Web: FastAPI

**Decisão**: Usar FastAPI como framework web principal.

**Alternativas Consideradas**:
- Flask: Mais simples, mas menos recursos nativos
- Django: Muito pesado para uma API
- Tornado: Boa performance, mas menos ecosistema

**Justificativa**:
```python
# FastAPI oferece validação automática e documentação
from pydantic import BaseModel

class SolicitacaoAnalise(BaseModel):
    codigo: str
    nivel_detalhamento: str = "intermediario"

@app.post("/analyze-code")
async def analisar_codigo(solicitacao: SolicitacaoAnalise):
    # Validação automática + documentação OpenAPI
    return await processar_analise(solicitacao)
```

**Benefícios Obtidos**:
- Validação automática de dados com Pydantic
- Documentação interativa automática (Swagger)
- Suporte nativo a async/await
- Performance superior ao Flask
- Type hints integrados

### Banco de Dados: PostgreSQL

**Decisão**: PostgreSQL como banco principal.

**Alternativas Consideradas**:
- MySQL: Menos recursos avançados
- SQLite: Não escalável para produção
- MongoDB: Não adequado para dados estruturados

**Justificativa**:
```sql
-- PostgreSQL oferece recursos avançados como JSONB
CREATE TABLE analysis_history (
    id SERIAL PRIMARY KEY,
    code_snippet TEXT NOT NULL,
    suggestions JSONB NOT NULL,  -- Flexibilidade + performance
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices em campos JSONB para performance
CREATE INDEX idx_suggestions_type ON analysis_history 
USING GIN ((suggestions -> 'tipo'));
```

**Benefícios Obtidos**:
- JSONB para dados semi-estruturados (sugestões)
- Transações ACID confiáveis
- Excelente performance com índices apropriados
- Recursos avançados (particionamento, replicação)
- Comunidade ativa e documentação extensa

### Cache: Redis

**Decisão**: Redis para cache distribuído.

**Alternativas Consideradas**:
- Memcached: Menos recursos
- Cache em memória: Não compartilhado entre instâncias
- Database cache: Muito lento

**Justificativa**:
```python
# Redis permite estruturas de dados complexas
import redis.asyncio as redis

class GerenciadorCache:
    async def salvar_analise_cache(self, codigo: str, resultado: dict):
        hash_codigo = hashlib.sha256(codigo.encode()).hexdigest()
        
        # Serialização eficiente com pickle
        dados_cache = {
            'resultado': resultado,
            'timestamp': datetime.now().isoformat(),
            'hash_codigo': hash_codigo
        }
        
        # TTL automático
        await self.redis_client.setex(
            f"analise:{hash_codigo}", 
            3600,  # 1 hora
            pickle.dumps(dados_cache)
        )
```

**Benefícios Obtidos**:
- Cache distribuído entre múltiplas instâncias
- TTL automático para limpeza
- Estruturas de dados avançadas
- Persistência opcional
- Monitoramento integrado

### Orquestração: Crew AI

**Decisão**: Integração com Crew AI para orquestração de agentes.

**Alternativas Consideradas**:
- Celery: Apenas filas, não orquestração inteligente
- Airflow: Muito pesado para este caso
- Implementação própria: Muito tempo de desenvolvimento

**Justificativa**:
```python
# Crew AI permite agentes especializados
from crewai import Agent, Task, Crew

performance_agent = Agent(
    role='Especialista em Performance',
    goal='Identificar gargalos e otimizações',
    backstory='10 anos otimizando código Python',
    tools=[ast_analyzer, profiler]
)

security_agent = Agent(
    role='Auditor de Segurança',
    goal='Identificar vulnerabilidades',
    backstory='Especialista em segurança de aplicações',
    tools=[security_scanner, vulnerability_db]
)

# Workflow colaborativo
crew = Crew(
    agents=[performance_agent, security_agent],
    tasks=[performance_task, security_task],
    process=Process.sequential
)
```

**Benefícios Obtidos**:
- Especialização de agentes por domínio
- Workflows flexíveis e configuráveis
- Colaboração entre agentes
- Rastreabilidade de decisões
- Escalabilidade horizontal

## 🏗️ Decisões de Arquitetura

### Arquitetura em Camadas

**Decisão**: Implementar arquitetura em camadas bem definidas.

```
┌─────────────────┐
│   API Layer     │  ← FastAPI, validação, serialização
├─────────────────┤
│ Business Logic  │  ← Analisador, orquestrador, regras
├─────────────────┤
│  Data Access    │  ← Repositórios, cache, banco
├─────────────────┤
│ Infrastructure  │  ← Monitoramento, logging, config
└─────────────────┘
```

**Justificativa**:
- Separação clara de responsabilidades
- Facilita testes unitários
- Permite evolução independente de camadas
- Melhora manutenibilidade

### Padrão Repository

**Decisão**: Usar padrão Repository para acesso a dados.

```python
# Abstração do acesso a dados
class RepositorioAnalises:
    async def salvar(self, analise: Analise) -> int:
        raise NotImplementedError
    
    async def buscar_por_id(self, id: int) -> Optional[Analise]:
        raise NotImplementedError

class RepositorioAnalisesPG(RepositorioAnalises):
    async def salvar(self, analise: Analise) -> int:
        # Implementação específica do PostgreSQL
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "INSERT INTO analysis_history (...) VALUES (...) RETURNING id",
                analise.codigo, analise.sugestoes
            )
```

**Benefícios**:
- Testabilidade com mocks
- Flexibilidade para trocar implementações
- Código de negócio independente de infraestrutura

### Dependency Injection

**Decisão**: Usar injeção de dependência com FastAPI.

```python
# Configuração de dependências
async def get_database():
    return GerenciadorBancoDados()

async def get_cache():
    return gerenciador_cache

async def get_analisador(
    db: GerenciadorBancoDados = Depends(get_database),
    cache: GerenciadorCache = Depends(get_cache)
):
    return AnalisadorCodigo(db, cache)

# Uso nos endpoints
@app.post("/analyze-code")
async def analisar_codigo(
    solicitacao: SolicitacaoAnalise,
    analisador: AnalisadorCodigo = Depends(get_analisador)
):
    return await analisador.analisar(solicitacao)
```

**Benefícios**:
- Facilita testes com mocks
- Configuração centralizada
- Lifecycle management automático

## 🔍 Decisões de Implementação

### Análise de Código: AST vs Regex

**Decisão**: Usar AST (Abstract Syntax Tree) como base da análise.

**Alternativas Consideradas**:
- Regex: Rápido mas limitado e propenso a erros
- Parsing manual: Muito complexo
- Ferramentas externas: Dependências pesadas

**Justificativa**:
```python
import ast

def analisar_complexidade(codigo: str) -> int:
    """Análise precisa usando AST."""
    tree = ast.parse(codigo)
    complexidade = 1
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For)):
            complexidade += 1
        elif isinstance(node, ast.BoolOp):
            complexidade += len(node.values) - 1
    
    return complexidade

# vs Regex (impreciso)
def analisar_complexidade_regex(codigo: str) -> int:
    """Análise imprecisa com regex."""
    import re
    ifs = len(re.findall(r'\bif\b', codigo))
    whiles = len(re.findall(r'\bwhile\b', codigo))
    # Não consegue distinguir contexto, strings, comentários...
    return ifs + whiles
```

**Benefícios do AST**:
- Análise precisa da estrutura do código
- Não confunde strings com código
- Acesso a informações semânticas
- Extensibilidade para novas análises

### Processamento Assíncrono

**Decisão**: Usar async/await para operações I/O.

```python
# Operações I/O assíncronas
async def analisar_codigo(self, codigo: str) -> List[Sugestao]:
    # Análise CPU-intensiva em thread pool
    sugestoes_ast = await asyncio.get_event_loop().run_in_executor(
        None, self._analisar_ast, codigo
    )
    
    # I/O assíncrono para cache
    cache_result = await self.cache.obter_analise_cache(codigo)
    
    # I/O assíncrono para banco
    await self.db.salvar_analise(codigo, sugestoes_ast)
    
    return sugestoes_ast
```

**Benefícios**:
- Melhor utilização de recursos
- Maior throughput
- Responsividade mantida durante operações longas

### Configuração: Environment Variables

**Decisão**: Usar variáveis de ambiente para configuração.

```python
import os
from dataclasses import dataclass

@dataclass
class ConfiguracaoBancoDados:
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    porta: int = int(os.getenv("POSTGRES_PORT", "5432"))
    nome_banco: str = os.getenv("POSTGRES_DB", "agente_otimizacao")
    usuario: str = os.getenv("POSTGRES_USER", "postgres")
    senha: str = os.getenv("POSTGRES_PASSWORD", "")
```

**Alternativas Consideradas**:
- Arquivos de configuração: Mais complexo para deploy
- Configuração hardcoded: Inflexível
- Configuração via API: Complexidade desnecessária

**Benefícios**:
- Compatível com containers
- Fácil para diferentes ambientes
- Segurança (senhas não no código)
- Padrão da indústria

## 📊 Decisões de Monitoramento

### Métricas: Prometheus + Custom Metrics

**Decisão**: Combinar Prometheus com métricas customizadas.

```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de negócio
ANALISES_TOTAL = Counter('analises_total', 'Total de análises')
TEMPO_ANALISE = Histogram('tempo_analise_segundos', 'Tempo de análise')
PONTUACAO_MEDIA = Gauge('pontuacao_media', 'Pontuação média de qualidade')

# Uso nas funções
async def analisar_codigo(self, codigo: str):
    with TEMPO_ANALISE.time():
        ANALISES_TOTAL.inc()
        resultado = await self._processar_analise(codigo)
        PONTUACAO_MEDIA.set(resultado.pontuacao)
        return resultado
```

**Benefícios**:
- Métricas padronizadas da indústria
- Integração com Grafana
- Alertas automáticos
- Histórico de performance

### Logging: Structured Logging

**Decisão**: Usar logging estruturado com JSON.

```python
import structlog

logger = structlog.get_logger()

async def analisar_codigo(self, codigo: str, nome_arquivo: str = None):
    logger.info(
        "analise_iniciada",
        tamanho_codigo=len(codigo),
        nome_arquivo=nome_arquivo,
        timestamp=datetime.now().isoformat()
    )
    
    try:
        resultado = await self._processar_analise(codigo)
        logger.info(
            "analise_concluida",
            pontuacao=resultado.pontuacao,
            numero_sugestoes=len(resultado.sugestoes),
            tempo_execucao=resultado.tempo_analise
        )
        return resultado
    except Exception as e:
        logger.error(
            "analise_falhou",
            erro=str(e),
            tipo_erro=type(e).__name__
        )
        raise
```

**Benefícios**:
- Logs facilmente parseáveis
- Correlação de eventos
- Análise automatizada
- Debugging eficiente

## 🔒 Decisões de Segurança

### Validação de Entrada

**Decisão**: Validação rigorosa em múltiplas camadas.

```python
from pydantic import BaseModel, validator

class SolicitacaoAnalise(BaseModel):
    codigo: str
    nome_arquivo: Optional[str] = None
    
    @validator('codigo')
    def validar_codigo(cls, v):
        if not v.strip():
            raise ValueError("Código não pode estar vazio")
        
        if len(v) > 50000:  # Limite de tamanho
            raise ValueError("Código muito grande")
        
        # Verificação básica de sintaxe
        try:
            compile(v, '<string>', 'exec')
        except SyntaxError as e:
            raise ValueError(f"Erro de sintaxe: {e}")
        
        return v

# Sanitização adicional
def sanitizar_codigo(codigo: str) -> str:
    """Remove construções potencialmente perigosas."""
    # Remove imports perigosos para análise
    linhas_seguras = []
    for linha in codigo.split('\n'):
        if not re.match(r'^\s*(import os|import subprocess)', linha):
            linhas_seguras.append(linha)
    
    return '\n'.join(linhas_seguras)
```

### Rate Limiting

**Decisão**: Implementar rate limiting por IP.

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze-code")
@limiter.limit("10/minute")  # 10 análises por minuto
async def analisar_codigo(request: Request, solicitacao: SolicitacaoAnalise):
    return await processar_analise(solicitacao)
```

## 🚀 Decisões de Performance

### Cache Strategy

**Decisão**: Cache hierárquico com TTL inteligente.

```python
class CacheHierarquico:
    def __init__(self):
        self.l1_cache = {}  # Memória local (mais rápido)
        self.l2_cache = redis_client  # Redis (compartilhado)
    
    async def obter(self, chave: str):
        # L1: Cache local
        if chave in self.l1_cache:
            return self.l1_cache[chave]
        
        # L2: Cache Redis
        valor = await self.l2_cache.get(chave)
        if valor:
            self.l1_cache[chave] = valor  # Promove para L1
            return valor
        
        return None
    
    async def salvar(self, chave: str, valor: Any, ttl: int = 3600):
        # TTL baseado no tipo de análise
        if "performance" in chave:
            ttl = 7200  # Cache mais longo para análises de performance
        elif "security" in chave:
            ttl = 1800  # Cache mais curto para segurança
        
        self.l1_cache[chave] = valor
        await self.l2_cache.setex(chave, ttl, pickle.dumps(valor))
```

### Connection Pooling

**Decisão**: Pool de conexões otimizado para carga.

```python
# Configuração baseada em carga esperada
DATABASE_CONFIG = {
    'pool_size': 20,        # Conexões base
    'max_overflow': 30,     # Conexões extras sob carga
    'pool_timeout': 30,     # Timeout para obter conexão
    'pool_recycle': 3600,   # Recicla conexões a cada hora
    'pool_pre_ping': True   # Verifica conexões antes de usar
}
```

## 🧪 Decisões de Teste

### Estratégia de Teste

**Decisão**: Pirâmide de testes com foco em testes unitários.

```
    /\
   /  \     E2E Tests (poucos, críticos)
  /____\
 /      \   Integration Tests (médio)
/________\  Unit Tests (muitos, rápidos)
```

```python
# Testes unitários com mocks
@pytest.mark.asyncio
async def test_analisar_codigo_com_cache():
    # Arrange
    mock_cache = AsyncMock()
    mock_cache.obter_analise_cache.return_value = None
    
    analisador = AnalisadorCodigo(cache=mock_cache)
    codigo = "def hello(): print('Hello')"
    
    # Act
    resultado = await analisador.analisar_codigo(codigo)
    
    # Assert
    assert isinstance(resultado, list)
    mock_cache.salvar_analise_cache.assert_called_once()

# Testes de integração com banco real
@pytest.mark.integration
async def test_salvar_e_recuperar_analise():
    bd = GerenciadorBancoDados()
    await bd.inicializar_banco()
    
    analise_id = await bd.salvar_analise("test", [], 85.0)
    analise = await bd.obter_analise_por_id(analise_id)
    
    assert analise['pontuacao_qualidade'] == 85.0
```

## 📈 Decisões de Escalabilidade

### Horizontal Scaling

**Decisão**: Design stateless para escalabilidade horizontal.

```python
# Aplicação stateless - estado no cache/banco
class AnalisadorCodigo:
    def __init__(self, cache: GerenciadorCache, db: GerenciadorBancoDados):
        self.cache = cache  # Estado compartilhado
        self.db = db        # Estado persistente
        # Sem estado local que impeça escalabilidade
    
    async def analisar_codigo(self, codigo: str):
        # Busca estado no cache compartilhado
        cache_key = self._gerar_chave_cache(codigo)
        resultado_cache = await self.cache.obter(cache_key)
        
        if resultado_cache:
            return resultado_cache
        
        # Processa e salva no estado compartilhado
        resultado = await self._processar_analise(codigo)
        await self.cache.salvar(cache_key, resultado)
        await self.db.salvar_analise(codigo, resultado)
        
        return resultado
```

### Load Balancing Strategy

**Decisão**: Load balancing baseado em least connections.

```nginx
# Nginx configurado para least_conn
upstream agente_backend {
    least_conn;  # Direciona para servidor com menos conexões
    server agente-1:8000 weight=1;
    server agente-2:8000 weight=1;
    server agente-3:8000 weight=2;  # Servidor mais potente
}
```

## 🔄 Decisões de Deploy

### Containerização

**Decisão**: Docker para consistência entre ambientes.

```dockerfile
# Multi-stage build para otimização
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# Usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash agente
USER agente

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks

**Decisão**: Health checks em múltiplas camadas.

```python
@app.get("/health/live")
async def liveness_check():
    """Verifica se a aplicação está viva."""
    return {"status": "alive", "timestamp": datetime.now()}

@app.get("/health/ready")
async def readiness_check():
    """Verifica se está pronto para receber tráfego."""
    checks = {
        "database": await verificar_banco(),
        "cache": await verificar_cache(),
        "disk_space": verificar_espaco_disco()
    }
    
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    
    return Response(
        content=json.dumps({
            "status": "ready" if all_ready else "not_ready",
            "checks": checks
        }),
        status_code=status_code
    )
```

## 🎯 Conclusão

Cada decisão técnica foi tomada considerando:

1. **Requisitos funcionais**: O que o sistema precisa fazer
2. **Requisitos não-funcionais**: Performance, escalabilidade, manutenibilidade
3. **Contexto do projeto**: Tempo, recursos, expertise da equipe
4. **Futuro**: Facilidade de evolução e manutenção

As decisões documentadas aqui formam a base técnica sólida do sistema, permitindo que ele atenda aos requisitos atuais e seja facilmente evoluído no futuro.

### Próximos Passos

- **Monitoramento contínuo** das decisões para validar eficácia
- **Refatoração incremental** quando necessário
- **Documentação atualizada** conforme o sistema evolui
- **Revisão periódica** das decisões técnicas

