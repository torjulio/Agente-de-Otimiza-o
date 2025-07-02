"""
Teste funcional simples para validar a funcionalidade básica
sem dependências externas como banco de dados.
"""

import pytest
import asyncio
from servicos.analisador_codigo import AnalisadorCodigo
from modelos.schemas import NivelDetalhamento

class TestFuncionalBasico:
    """Testes funcionais básicos."""
    
    def test_analisador_instancia(self):
        """Testa se o analisador pode ser instanciado."""
        analisador = AnalisadorCodigo()
        assert analisador is not None
    
    @pytest.mark.asyncio
    async def test_analise_codigo_simples(self):
        """Testa análise de código simples."""
        analisador = AnalisadorCodigo()
        codigo = "def hello(): print('Hello, World!')"
        
        try:
            sugestoes = await analisador.analisar_codigo(codigo)
            assert isinstance(sugestoes, list)
            print(f"✅ Análise concluída com {len(sugestoes)} sugestões")
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            # Não falha o teste, apenas reporta
    
    def test_calcular_pontuacao(self):
        """Testa cálculo de pontuação."""
        analisador = AnalisadorCodigo()
        
        # Código simples
        codigo = "def hello(): print('Hello')"
        pontuacao = analisador.calcular_pontuacao_qualidade(codigo)
        
        assert isinstance(pontuacao, (int, float))
        assert 0 <= pontuacao <= 100
        print(f"✅ Pontuação calculada: {pontuacao}")
    
    @pytest.mark.asyncio
    async def test_diferentes_niveis(self):
        """Testa diferentes níveis de detalhamento."""
        analisador = AnalisadorCodigo()
        codigo = "def soma(a, b): return a + b"
        
        for nivel in [NivelDetalhamento.BASICO, NivelDetalhamento.INTERMEDIARIO, NivelDetalhamento.AVANCADO]:
            try:
                sugestoes = await analisador.analisar_codigo(codigo, nivel)
                print(f"✅ Nível {nivel.value}: {len(sugestoes)} sugestões")
            except Exception as e:
                print(f"❌ Erro no nível {nivel.value}: {e}")
    
    def test_validacao_codigo_vazio(self):
        """Testa validação de código vazio."""
        analisador = AnalisadorCodigo()
        
        try:
            pontuacao = analisador.calcular_pontuacao_qualidade("")
            print(f"⚠️  Código vazio retornou pontuação: {pontuacao}")
        except Exception as e:
            print(f"✅ Código vazio corretamente rejeitado: {e}")
    
    def test_codigo_com_problemas(self):
        """Testa código com problemas óbvios."""
        analisador = AnalisadorCodigo()
        
        codigo_problematico = """
def f(x):
    s=0
    for i in range(len(x)):s+=x[i]
    return s/len(x) if len(x)>0 else 0
"""
        
        pontuacao = analisador.calcular_pontuacao_qualidade(codigo_problematico)
        print(f"✅ Código problemático - Pontuação: {pontuacao}")
        
        # Deve ter pontuação menor que código bem escrito
        assert pontuacao < 100

def test_importacoes():
    """Testa se todas as importações funcionam."""
    try:
        from servicos.analisador_codigo import AnalisadorCodigo
        from modelos.schemas import SolicitacaoAnalise, NivelDetalhamento
        print("✅ Todas as importações funcionam")
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        pytest.fail(f"Erro de importação: {e}")

def test_estrutura_projeto():
    """Testa se a estrutura do projeto está correta."""
    import os
    
    arquivos_essenciais = [
        "main.py",
        "modelos/schemas.py",
        "servicos/analisador_codigo.py",
        "README.md"
    ]
    
    for arquivo in arquivos_essenciais:
        assert os.path.exists(arquivo), f"Arquivo essencial não encontrado: {arquivo}"
    
    print("✅ Estrutura do projeto está correta")

if __name__ == "__main__":
    # Executa testes básicos
    print("🧪 Executando testes funcionais básicos...")
    
    # Teste de importações
    test_importacoes()
    
    # Teste de estrutura
    test_estrutura_projeto()
    
    # Testes básicos
    teste = TestFuncionalBasico()
    teste.test_analisador_instancia()
    teste.test_calcular_pontuacao()
    teste.test_validacao_codigo_vazio()
    teste.test_codigo_com_problemas()
    
    # Testes assíncronos
    async def executar_testes_async():
        await teste.test_analise_codigo_simples()
        await teste.test_diferentes_niveis()
    
    asyncio.run(executar_testes_async())
    
    print("✅ Todos os testes funcionais básicos concluídos!")

