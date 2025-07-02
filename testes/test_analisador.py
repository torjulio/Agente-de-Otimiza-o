"""
Testes unitários para o AnalisadorCodigo.

Testa a funcionalidade principal de análise de código Python,
incluindo detecção de problemas e geração de sugestões.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from servicos.analisador_codigo import AnalisadorCodigo
from modelos.schemas import NivelDetalhamento, TipoSugestao

class TestAnalisadorCodigo:
    """Testes para a classe AnalisadorCodigo."""
    
    @pytest.fixture
    def analisador(self):
        """Fixture que retorna uma instância do analisador."""
        return AnalisadorCodigo()
    
    @pytest.mark.asyncio
    async def test_analisar_codigo_simples(self, analisador):
        """Testa análise de código simples."""
        codigo = """
def hello():
    print("Hello, World!")
"""
        
        sugestoes = await analisador.analisar_codigo(codigo)
        
        assert isinstance(sugestoes, list)
        assert analisador.ultimo_tempo_analise > 0
    
    @pytest.mark.asyncio
    async def test_analisar_codigo_com_problemas_performance(self, analisador):
        """Testa detecção de problemas de performance."""
        codigo = """
def buscar_item(lista, item):
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1

numeros = []
for i in range(1000):
    numeros.append(i)
"""
        
        sugestoes = await analisador.analisar_codigo(
            codigo, 
            nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO,
            focar_performance=True
        )
        
        # Deve encontrar problemas de performance
        sugestoes_performance = [s for s in sugestoes if s.tipo == TipoSugestao.PERFORMANCE]
        assert len(sugestoes_performance) > 0
        
        # Deve sugerir list comprehension
        titulos = [s.titulo for s in sugestoes_performance]
        assert any("comprehension" in titulo.lower() for titulo in titulos)
    
    @pytest.mark.asyncio
    async def test_analisar_codigo_com_problemas_legibilidade(self, analisador):
        """Testa detecção de problemas de legibilidade."""
        codigo = """
                def f(x,y,z):
                    a=x+y
                    b=z*2
                    if a>b:return a
                    else:return b
                """
        
        sugestoes = await analisador.analisar_codigo(codigo)
        
        # Deve encontrar problemas de legibilidade
        sugestoes_legibilidade = [s for s in sugestoes if s.tipo == TipoSugestao.LEGIBILIDADE]
        assert len(sugestoes_legibilidade) > 0
    
    @pytest.mark.asyncio
    async def test_analisar_codigo_com_problemas_seguranca(self, analisador):
        """Testa detecção de problemas de segurança."""
        codigo = """
            import os
            user_input = input("Digite um comando: ")
            eval(user_input)  # Muito perigoso!

            query = "SELECT * FROM users WHERE id = " + user_id
            cursor.execute(query)  # SQL injection
            """
        
        sugestoes = await analisador.analisar_codigo(
            codigo,
            nivel_detalhamento=NivelDetalhamento.AVANCADO
        )
        
        # Deve encontrar problemas de segurança
        sugestoes_seguranca = [s for s in sugestoes if s.tipo == TipoSugestao.SEGURANCA]
        assert len(sugestoes_seguranca) > 0
        
        # Deve detectar uso de eval
        titulos = [s.titulo for s in sugestoes_seguranca]
        assert any("eval" in titulo.lower() for titulo in titulos)
    
    @pytest.mark.asyncio
    async def test_analisar_codigo_com_boas_praticas(self, analisador):
        """Testa detecção de problemas de boas práticas."""
        codigo = """
            def calcular_area(raio):
                return 3.14159 * raio ** 2

            class MinhaClasse:
                def metodo_sem_docstring(self):
                    try:
                        resultado = 10 / 0
                    except:  # Exceção genérica
                        pass
            """
        
        sugestoes = await analisador.analisar_codigo(
            codigo,
            nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO
        )
        
        # Deve encontrar problemas de boas práticas
        sugestoes_boas_praticas = [s for s in sugestoes if s.tipo == TipoSugestao.BOAS_PRATICAS]
        assert len(sugestoes_boas_praticas) > 0
    
    @pytest.mark.asyncio
    async def test_niveis_detalhamento(self, analisador):
        """Testa diferentes níveis de detalhamento."""
        codigo = """
                def funcao_complexa(dados):
                    resultado = []
                    for item in dados:
                        if item > 0:
                            for i in range(item):
                                if i % 2 == 0:
                                    resultado.append(i * 2)
                    return resultado
                """
        
        # Análise básica
        sugestoes_basico = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.BASICO
        )
        
        # Análise intermediária
        sugestoes_intermediario = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.INTERMEDIARIO
        )
        
        # Análise avançada
        sugestoes_avancado = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.AVANCADO
        )
        
        # Análise avançada deve ter mais sugestões
        assert len(sugestoes_avancado) >= len(sugestoes_intermediario)
        assert len(sugestoes_intermediario) >= len(sugestoes_basico)
    
    def test_calcular_pontuacao_qualidade(self, analisador):
        """Testa cálculo de pontuação de qualidade."""
        # Código de boa qualidade
        codigo_bom = """
def calcular_media(numeros: List[float]) -> float:
    \"\"\"
    Calcula a média aritmética de uma lista de números.
    
    Args:
        numeros: Lista de números para calcular a média
        
    Returns:
        A média aritmética dos números
    \"\"\"
    if not numeros:
        return 0.0
    
    return sum(numeros) / len(numeros)
"""
        
        # Código de qualidade ruim
        codigo_ruim = """
def f(x):
    s=0
    for i in range(len(x)):s+=x[i]
    return s/len(x) if len(x)>0 else 0
"""
        
        pontuacao_boa = analisador.calcular_pontuacao_qualidade(codigo_bom)
        pontuacao_ruim = analisador.calcular_pontuacao_qualidade(codigo_ruim)
        
        assert 0 <= pontuacao_boa <= 100
        assert 0 <= pontuacao_ruim <= 100
        assert pontuacao_boa > pontuacao_ruim
    
    @pytest.mark.asyncio
    async def test_codigo_vazio(self, analisador):
        """Testa comportamento com código vazio."""
        with pytest.raises(ValueError, match="Código não pode estar vazio"):
            await analisador.analisar_codigo("")
    
    @pytest.mark.asyncio
    async def test_codigo_com_erro_sintaxe(self, analisador):
        """Testa comportamento com erro de sintaxe."""
        codigo_invalido = """
def funcao_invalida(
    # Parênteses não fechados
"""
        
        with pytest.raises(Exception):  # Deve levantar exceção de sintaxe
            await analisador.analisar_codigo(codigo_invalido)
    
    @pytest.mark.asyncio
    async def test_ordenacao_sugestoes_por_prioridade(self, analisador):
        """Testa se sugestões são ordenadas por prioridade."""
        codigo = """
def funcao_com_varios_problemas():
    eval("print('perigoso')")  # Alta prioridade (segurança)
    x = 1  # Baixa prioridade (nome de variável)
    for i in range(len(lista)):  # Média prioridade (performance)
        pass
"""
        
        sugestoes = await analisador.analisar_codigo(
            codigo,
            nivel_detalhamento=NivelDetalhamento.AVANCADO
        )
        
        # Verifica se estão ordenadas por prioridade (decrescente)
        if len(sugestoes) > 1:
            for i in range(len(sugestoes) - 1):
                assert sugestoes[i].prioridade >= sugestoes[i + 1].prioridade
    
    @pytest.mark.asyncio
    async def test_limite_sugestoes_por_nivel(self, analisador):
        """Testa se o número de sugestões é limitado por nível."""
        # Código com muitos problemas
        codigo = """
def f1(x): return x+1
def f2(x): return x+2
def f3(x): return x+3
def f4(x): return x+4
def f5(x): return x+5
def f6(x): return x+6
def f7(x): return x+7
def f8(x): return x+8
def f9(x): return x+9
def f10(x): return x+10
def f11(x): return x+11
def f12(x): return x+12
"""
        
        sugestoes_basico = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.BASICO
        )
        sugestoes_intermediario = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.INTERMEDIARIO
        )
        sugestoes_avancado = await analisador.analisar_codigo(
            codigo, NivelDetalhamento.AVANCADO
        )
        
        # Verifica limites
        assert len(sugestoes_basico) <= 5
        assert len(sugestoes_intermediario) <= 10
        assert len(sugestoes_avancado) <= 20
    
    def test_contar_loops_aninhados(self, analisador):
        """Testa contagem de loops aninhados."""
        import ast
        
        codigo_simples = """
for i in range(10):
    print(i)
"""
        
        codigo_aninhado = """
for i in range(10):
    for j in range(10):
        for k in range(10):
            print(i, j, k)
"""
        
        tree_simples = ast.parse(codigo_simples)
        tree_aninhado = ast.parse(codigo_aninhado)
        
        # Encontra os nós de loop
        loop_simples = None
        loop_aninhado = None
        
        for node in ast.walk(tree_simples):
            if isinstance(node, ast.For):
                loop_simples = node
                break
        
        for node in ast.walk(tree_aninhado):
            if isinstance(node, ast.For):
                loop_aninhado = node
                break
        
        nivel_simples = analisador._contar_loops_aninhados(loop_simples)
        nivel_aninhado = analisador._contar_loops_aninhados(loop_aninhado)
        
        assert nivel_simples == 0  # Sem aninhamento
        assert nivel_aninhado >= 2  # Pelo menos 2 níveis de aninhamento
    
    def test_calcular_complexidade_ciclomatica(self, analisador):
        """Testa cálculo de complexidade ciclomática."""
        import ast
        
        # Função simples (complexidade 1)
        codigo_simples = """
def funcao_simples():
    return 42
"""
        
        # Função complexa (complexidade alta)
        codigo_complexo = """
def funcao_complexa(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        for i in range(abs(x)):
            if i % 2 == 0:
                y += i
        return y
    else:
        return 0
"""
        
        tree_simples = ast.parse(codigo_simples)
        tree_complexo = ast.parse(codigo_complexo)
        
        func_simples = None
        func_complexa = None
        
        for node in ast.walk(tree_simples):
            if isinstance(node, ast.FunctionDef):
                func_simples = node
                break
        
        for node in ast.walk(tree_complexo):
            if isinstance(node, ast.FunctionDef):
                func_complexa = node
                break
        
        complexidade_simples = analisador._calcular_complexidade_ciclomatica(func_simples)
        complexidade_complexa = analisador._calcular_complexidade_ciclomatica(func_complexa)
        
        assert complexidade_simples == 1
        assert complexidade_complexa > complexidade_simples

@pytest.mark.asyncio
async def test_performance_analise_codigo_grande():
    """Testa performance com código grande."""
    analisador = AnalisadorCodigo()
    
    # Gera código grande
    codigo_grande = """
def funcao_grande():
    resultado = []
""" + "\n".join([f"    resultado.append({i})" for i in range(1000)]) + """
    return resultado
"""
    
    inicio = datetime.now()
    sugestoes = await analisador.analisar_codigo(codigo_grande)
    fim = datetime.now()
    
    tempo_execucao = (fim - inicio).total_seconds()
    
    # Deve completar em tempo razoável (menos de 10 segundos)
    assert tempo_execucao < 10.0
    assert isinstance(sugestoes, list)

if __name__ == "__main__":
    # Executa testes se rodado diretamente
    pytest.main([__file__, "-v"])

