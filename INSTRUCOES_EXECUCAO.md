# 🚀 Instruções de Execução - Agente de Otimização de Código

## ⚡ Execução Rápida (Demonstração)

Para uma demonstração rápida das funcionalidades principais:

```bash
# 1. Navegue até o diretório do projeto
cd agente_otimizacao_codigo

# 2. Execute a demonstração
python demo_sistema.py
```

Esta demonstração mostra:
- ✅ Análise básica de código
- ✅ Diferentes níveis de detalhamento
- ✅ Detecção de tipos de problemas
- ✅ Sistema de pontuação de qualidade

## 🔧 Execução da API (Desenvolvimento)

Para executar a API REST completa:

```bash
# 1. Instale as dependências básicas
pip install fastapi uvicorn pydantic sqlalchemy psycopg2-binary asyncpg redis structlog psutil

# 2. Execute a API
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Acesse a documentação
# http://localhost:8000/documentacao
```

### Endpoints Disponíveis:
- `GET /health` - Status da aplicação
- `POST /analyze-code` - Análise de código
- `GET /historico` - Histórico de análises
- `GET /estatisticas` - Estatísticas do sistema
- `GET /documentacao` - Documentação interativa

## 🐳 Execução com Docker (Produção)

Para ambiente completo com todos os serviços:

```bash
# 1. Execute com Docker Compose
docker-compose up -d

# 2. Aguarde os serviços iniciarem
docker-compose logs -f

# 3. Acesse a aplicação
# http://localhost:8000
```

## 🧪 Execução dos Testes

Para validar o funcionamento:

```bash
# Testes funcionais básicos
python testes/test_funcional.py

# Testes da API (requer dependências)
python -m pytest testes/test_api_simples.py -v

# Todos os testes
python -m pytest testes/ -v
```

## 📋 Exemplo de Uso da API

```bash
# Teste básico de saúde
curl http://localhost:8000/health

# Análise de código
curl -X POST "http://localhost:8000/analyze-code" \
     -H "Content-Type: application/json" \
     -d '{
       "codigo": "def hello(): print(\"Hello, World!\")",
       "nivel_detalhamento": "intermediario"
     }'
```

## 🔍 Verificação do Sistema

Para verificar se tudo está funcionando:

1. **Health Check**: `curl http://localhost:8000/health`
2. **Documentação**: Acesse `http://localhost:8000/documentacao`
3. **Demonstração**: Execute `python demo_sistema.py`

## ⚠️ Solução de Problemas

### Erro de Módulo Não Encontrado
```bash
# Adicione o diretório ao PYTHONPATH
export PYTHONPATH=/caminho/para/agente_otimizacao_codigo:$PYTHONPATH
```

### Erro de Dependências
```bash
# Instale dependências uma por uma
pip install fastapi uvicorn pydantic
```

### Erro de Banco de Dados
- A aplicação funciona sem banco de dados
- Para funcionalidade completa, configure PostgreSQL conforme docker-compose.yml

## 📚 Próximos Passos

1. **Explore a Documentação**: Leia o README.md completo
2. **Teste a API**: Use a documentação interativa
3. **Personalize**: Modifique as regras de análise conforme necessário
4. **Integre**: Use a API em seus projetos

---

**Nota**: O sistema foi projetado para funcionar mesmo sem todas as dependências externas (banco, cache) para facilitar a demonstração e testes.

