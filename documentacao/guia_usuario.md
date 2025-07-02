# 📚 Guia do Usuário - Agente de Otimização de Código Python

## Bem-vindo ao seu Assistente Pessoal de Código!

Olá! Se você chegou até aqui, provavelmente está procurando uma forma de melhorar a qualidade do seu código Python. Você está no lugar certo! Este guia vai te ensinar tudo o que você precisa saber para usar o Agente de Otimização de Código de forma eficiente e aproveitar ao máximo suas funcionalidades.

## 🎯 O que este Agente faz por você?

Imagine ter um colega experiente sempre ao seu lado, pronto para revisar seu código e dar sugestões valiosas. É exatamente isso que nosso agente faz! Ele:

- **Analisa seu código Python** em segundos
- **Identifica problemas** que você pode ter perdido
- **Sugere melhorias** específicas e práticas
- **Explica o porquê** de cada sugestão
- **Aprende com o tempo** para dar sugestões cada vez melhores

## 🚀 Primeiros Passos

### Seu Primeiro Teste

Vamos começar com algo simples. Aqui está um código que todos nós já escrevemos:

```python
def calcular_media(numeros):
    soma = 0
    for i in range(len(numeros)):
        soma = soma + numeros[i]
    return soma / len(numeros)

lista = [1, 2, 3, 4, 5]
resultado = calcular_media(lista)
print(resultado)
```

Parece funcional, certo? Mas nosso agente pode encontrar várias melhorias! Vamos ver como analisar este código.

### Usando a Interface Web (Mais Fácil)

Se você tem acesso à interface web:

1. **Abra seu navegador** e vá para `http://localhost:8000/dashboard`
2. **Cole seu código** na área de texto
3. **Escolha o nível de análise**:
   - **Básico**: Para uma revisão rápida
   - **Intermediário**: Para análise balanceada (recomendado)
   - **Avançado**: Para análise completa e detalhada
4. **Clique em "Analisar"** e aguarde alguns segundos
5. **Veja os resultados** organizados por categoria

### Usando a API (Para Desenvolvedores)

Se você prefere usar a API diretamente:

```python
import requests

# Seu código para análise
codigo = """
def calcular_media(numeros):
    soma = 0
    for i in range(len(numeros)):
        soma = soma + numeros[i]
    return soma / len(numeros)

lista = [1, 2, 3, 4, 5]
resultado = calcular_media(lista)
print(resultado)
"""

# Enviar para análise
response = requests.post(
    "http://localhost:8000/analyze-code",
    json={
        "codigo": codigo,
        "nome_arquivo": "minha_funcao.py",
        "nivel_detalhamento": "intermediario"
    }
)

# Ver os resultados
resultado = response.json()
print(f"Pontuação de qualidade: {resultado['pontuacao_qualidade']}/100")
print(f"Encontradas {len(resultado['sugestoes'])} sugestões de melhoria")
```

## 📊 Entendendo os Resultados

### Pontuação de Qualidade

A pontuação vai de 0 a 100 e representa a qualidade geral do seu código:

- **90-100**: Excelente! Seu código está muito bem escrito
- **80-89**: Bom! Algumas melhorias podem ser feitas
- **70-79**: Razoável, mas há espaço para melhorias importantes
- **60-69**: Precisa de atenção, várias melhorias necessárias
- **Abaixo de 60**: Requer refatoração significativa

### Tipos de Sugestões

#### 🚀 Performance
Melhorias que fazem seu código rodar mais rápido:

**Exemplo**: "Use list comprehension em vez de loop tradicional"
```python
# Antes (mais lento)
resultado = []
for x in lista:
    if x > 0:
        resultado.append(x * 2)

# Depois (mais rápido)
resultado = [x * 2 for x in lista if x > 0]
```

#### 📖 Legibilidade
Mudanças que tornam seu código mais fácil de entender:

**Exemplo**: "Use nomes mais descritivos para variáveis"
```python
# Antes (confuso)
def calc(l):
    s = 0
    for i in l:
        s += i
    return s

# Depois (claro)
def calcular_soma(numeros):
    soma_total = 0
    for numero in numeros:
        soma_total += numero
    return soma_total
```

#### ✅ Boas Práticas
Sugestões para seguir convenções Python:

**Exemplo**: "Adicione docstrings às suas funções"
```python
# Antes
def calcular_area(raio):
    return 3.14159 * raio ** 2

# Depois
def calcular_area(raio):
    """
    Calcula a área de um círculo.
    
    Args:
        raio (float): O raio do círculo
        
    Returns:
        float: A área do círculo
    """
    return 3.14159 * raio ** 2
```

#### 🔒 Segurança
Identificação de possíveis vulnerabilidades:

**Exemplo**: "Evite usar eval() com entrada do usuário"
```python
# Antes (perigoso)
entrada_usuario = input("Digite uma expressão: ")
resultado = eval(entrada_usuario)  # Muito perigoso!

# Depois (seguro)
import ast
entrada_usuario = input("Digite um número: ")
try:
    numero = float(entrada_usuario)
    resultado = numero * 2
except ValueError:
    print("Entrada inválida")
```

### Níveis de Prioridade

Cada sugestão tem uma prioridade de 1 a 10:

- **9-10**: Crítico - Corrija imediatamente
- **7-8**: Alto - Corrija em breve
- **5-6**: Médio - Considere corrigir
- **3-4**: Baixo - Melhoria opcional
- **1-2**: Cosmético - Quando tiver tempo

## 🎨 Personalizando sua Análise

### Foco em Performance

Se você está trabalhando em código que precisa ser muito rápido:

```python
response = requests.post(
    "http://localhost:8000/analyze-code",
    json={
        "codigo": seu_codigo,
        "focar_performance": True,  # Prioriza sugestões de velocidade
        "nivel_detalhamento": "avancado"
    }
)
```

### Análise por Arquivo

Para analisar arquivos específicos do seu projeto:

```python
def analisar_arquivo(caminho):
    with open(caminho, 'r') as arquivo:
        codigo = arquivo.read()
    
    response = requests.post(
        "http://localhost:8000/analyze-code",
        json={
            "codigo": codigo,
            "nome_arquivo": caminho,
            "nivel_detalhamento": "intermediario"
        }
    )
    
    return response.json()

# Analisar múltiplos arquivos
arquivos = ["main.py", "utils.py", "models.py"]
for arquivo in arquivos:
    resultado = analisar_arquivo(arquivo)
    print(f"\n{arquivo}: {resultado['pontuacao_qualidade']}/100")
```

## 📈 Acompanhando seu Progresso

### Histórico de Análises

Veja como seu código tem melhorado ao longo do tempo:

```python
# Obter histórico das últimas análises
response = requests.get("http://localhost:8000/historico?limite=20")
historico = response.json()

# Calcular tendência de melhoria
pontuacoes = [analise['pontuacao_qualidade'] for analise in historico]
if len(pontuacoes) > 1:
    melhoria = pontuacoes[0] - pontuacoes[-1]  # Mais recente - mais antiga
    print(f"Sua pontuação melhorou {melhoria:.1f} pontos!")
```

### Estatísticas Pessoais

```python
# Ver suas estatísticas gerais
response = requests.get("http://localhost:8000/estatisticas")
stats = response.json()

print(f"Total de análises: {stats['total_analises']}")
print(f"Pontuação média: {stats['media_pontuacao']:.1f}")
print(f"Tipos de problemas mais comuns:")
for tipo, quantidade in stats['tipos_sugestoes_mais_comuns'].items():
    print(f"  - {tipo}: {quantidade}")
```

## 🛠️ Casos de Uso Práticos

### 1. Revisão Antes do Commit

Integre o agente no seu workflow de desenvolvimento:

```bash
#!/bin/bash
# script: revisar_codigo.sh

echo "Analisando arquivos modificados..."
for arquivo in $(git diff --name-only --cached | grep "\.py$"); do
    echo "Analisando $arquivo..."
    python -c "
import requests
with open('$arquivo', 'r') as f:
    codigo = f.read()
response = requests.post('http://localhost:8000/analyze-code', 
    json={'codigo': codigo, 'nome_arquivo': '$arquivo'})
resultado = response.json()
print(f'Pontuação: {resultado[\"pontuacao_qualidade\"]}/100')
if resultado['pontuacao_qualidade'] < 80:
    print('⚠️  Considere melhorar este arquivo antes do commit')
    exit(1)
"
done
echo "✅ Todos os arquivos passaram na revisão!"
```

### 2. Análise de Projeto Completo

Para analisar um projeto inteiro:

```python
import os
import requests
from pathlib import Path

def analisar_projeto(diretorio):
    """Analisa todos os arquivos Python de um projeto."""
    resultados = []
    
    for arquivo_py in Path(diretorio).rglob("*.py"):
        if "venv" in str(arquivo_py) or "__pycache__" in str(arquivo_py):
            continue  # Pula arquivos de ambiente virtual
            
        try:
            with open(arquivo_py, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            response = requests.post(
                "http://localhost:8000/analyze-code",
                json={
                    "codigo": codigo,
                    "nome_arquivo": str(arquivo_py),
                    "nivel_detalhamento": "intermediario"
                }
            )
            
            if response.status_code == 200:
                resultado = response.json()
                resultados.append({
                    'arquivo': str(arquivo_py),
                    'pontuacao': resultado['pontuacao_qualidade'],
                    'sugestoes': len(resultado['sugestoes'])
                })
                print(f"✅ {arquivo_py}: {resultado['pontuacao_qualidade']:.1f}/100")
            else:
                print(f"❌ Erro ao analisar {arquivo_py}")
                
        except Exception as e:
            print(f"❌ Erro ao ler {arquivo_py}: {e}")
    
    return resultados

# Usar a função
resultados = analisar_projeto("./meu_projeto")

# Relatório final
pontuacao_media = sum(r['pontuacao'] for r in resultados) / len(resultados)
print(f"\n📊 Relatório do Projeto:")
print(f"Arquivos analisados: {len(resultados)}")
print(f"Pontuação média: {pontuacao_media:.1f}/100")

# Arquivos que precisam de mais atenção
print(f"\n🔧 Arquivos que precisam de atenção:")
for resultado in sorted(resultados, key=lambda x: x['pontuacao']):
    if resultado['pontuacao'] < 80:
        print(f"  - {resultado['arquivo']}: {resultado['pontuacao']:.1f}/100")
```

### 3. Monitoramento Contínuo

Para projetos em produção, monitore a qualidade continuamente:

```python
import time
import schedule
import requests

def verificar_qualidade_diaria():
    """Verifica a qualidade do código diariamente."""
    # Analisar arquivos principais
    arquivos_principais = ["main.py", "core.py", "utils.py"]
    
    pontuacoes = []
    for arquivo in arquivos_principais:
        try:
            with open(arquivo, 'r') as f:
                codigo = f.read()
            
            response = requests.post(
                "http://localhost:8000/analyze-code",
                json={"codigo": codigo, "nome_arquivo": arquivo}
            )
            
            if response.status_code == 200:
                pontuacao = response.json()['pontuacao_qualidade']
                pontuacoes.append(pontuacao)
        except:
            continue
    
    if pontuacoes:
        media = sum(pontuacoes) / len(pontuacoes)
        print(f"📊 Qualidade média hoje: {media:.1f}/100")
        
        if media < 75:
            print("⚠️  Alerta: Qualidade do código abaixo do esperado!")
            # Aqui você poderia enviar um email ou notificação

# Agendar verificação diária às 9h
schedule.every().day.at("09:00").do(verificar_qualidade_diaria)

# Manter o script rodando
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🎓 Dicas de Ouro

### 1. Comece Pequeno
Não tente corrigir tudo de uma vez. Comece com:
- Sugestões de prioridade alta (8-10)
- Problemas de segurança
- Melhorias simples de legibilidade

### 2. Entenda o "Porquê"
Cada sugestão vem com uma explicação. Leia e entenda o motivo antes de aplicar a mudança.

### 3. Use o Histórico
Acompanhe seu progresso ao longo do tempo. É motivador ver sua pontuação melhorando!

### 4. Personalize para seu Contexto
- Código de produção: Foque em performance e segurança
- Código de aprendizado: Foque em legibilidade e boas práticas
- Protótipos: Análise básica pode ser suficiente

### 5. Integre ao seu Workflow
- Pre-commit hooks para verificação automática
- CI/CD pipeline para análise contínua
- Revisões de código assistidas pelo agente

## ❓ Perguntas Frequentes

### "O agente vai substituir a revisão humana?"
Não! O agente é um assistente que complementa a revisão humana. Ele encontra problemas técnicos, mas a revisão humana ainda é essencial para lógica de negócio, arquitetura e contexto.

### "Posso confiar 100% nas sugestões?"
As sugestões são baseadas em boas práticas estabelecidas, mas sempre use seu julgamento. Algumas sugestões podem não se aplicar ao seu contexto específico.

### "Como o agente aprende?"
O agente usa padrões estabelecidos da comunidade Python e análise estática do código. Ele não "aprende" com seus dados específicos, garantindo privacidade.

### "Funciona com qualquer código Python?"
Sim! O agente analisa desde scripts simples até aplicações complexas. Quanto maior o código, mais detalhada será a análise.

### "E se eu discordar de uma sugestão?"
Tudo bem! Nem toda sugestão precisa ser aplicada. Use as que fazem sentido para seu projeto e contexto.

## 🆘 Precisa de Ajuda?

### Problemas Comuns

**"Erro 422 - Validation Error"**
- Verifique se o código está em formato de string válido
- Certifique-se de que não há caracteres especiais problemáticos

**"Análise muito lenta"**
- Use nível "básico" para códigos muito grandes
- Considere analisar arquivos menores separadamente

**"Muitas sugestões"**
- Comece com prioridade alta (8-10)
- Use filtros para focar em tipos específicos


## 🎉 Conclusão

Parabéns! Agora você sabe como usar o Agente de Otimização de Código para melhorar significativamente a qualidade do seu código Python. Lembre-se:

- **Comece pequeno** e vá evoluindo
- **Entenda as sugestões** antes de aplicá-las
- **Acompanhe seu progresso** ao longo do tempo
- **Integre ao seu workflow** para máximo benefício

O código de qualidade não é um destino, é uma jornada. E agora você tem um companheiro confiável para essa jornada!

Bom código! 🚀

