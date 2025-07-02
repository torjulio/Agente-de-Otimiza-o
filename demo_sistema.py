#!/usr/bin/env python3
"""
Demonstração funcional do Agente de Otimização de Código Python.

Este script demonstra as principais funcionalidades do sistema
sem depender de configurações complexas de banco de dados.
"""

import asyncio
import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from servicos.analisador_codigo import AnalisadorCodigo
from modelos.schemas import NivelDetalhamento

def print_header(titulo):
    """Imprime cabeçalho formatado."""
    print("\n" + "="*60)
    print(f"  {titulo}")
    print("="*60)

def print_sugestao(sugestao, indice):
    """Imprime uma sugestão formatada."""
    print(f"\n📋 Sugestão {indice + 1}:")
    print(f"   Tipo: {sugestao.tipo.value}")
    print(f"   Título: {sugestao.titulo}")
    print(f"   Prioridade: {sugestao.prioridade}/10")
    print(f"   Impacto: {sugestao.impacto.value}")
    print(f"   Descrição: {sugestao.descricao}")
    
    if sugestao.codigo_sugerido:
        print(f"   💡 Código sugerido:")
        print(f"   {sugestao.codigo_sugerido}")

async def demonstrar_analise_basica():
    """Demonstra análise básica de código."""
    print_header("DEMONSTRAÇÃO: ANÁLISE BÁSICA DE CÓDIGO")
    
    analisador = AnalisadorCodigo()
    
    codigo_exemplo = """
def calcular_media(numeros):
    soma = 0
    for i in range(len(numeros)):
        soma = soma + numeros[i]
    return soma / len(numeros)

lista = [1, 2, 3, 4, 5]
resultado = calcular_media(lista)
print(resultado)
"""
    
    print("📝 Código a ser analisado:")
    print(codigo_exemplo)
    
    print("\n🔍 Executando análise...")
    inicio = datetime.now()
    
    try:
        sugestoes = await analisador.analisar_codigo(
            codigo_exemplo,
            nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO
        )
        
        fim = datetime.now()
        tempo_analise = (fim - inicio).total_seconds()
        
        pontuacao = analisador.calcular_pontuacao_qualidade(codigo_exemplo)
        
        print(f"✅ Análise concluída em {tempo_analise:.2f} segundos")
        print(f"📊 Pontuação de qualidade: {pontuacao:.1f}/100")
        print(f"📋 Sugestões encontradas: {len(sugestoes)}")
        
        # Mostra as sugestões
        for i, sugestao in enumerate(sugestoes[:3]):  # Mostra apenas as 3 primeiras
            print_sugestao(sugestao, i)
        
        if len(sugestoes) > 3:
            print(f"\n... e mais {len(sugestoes) - 3} sugestões")
            
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")

async def demonstrar_diferentes_niveis():
    """Demonstra análise com diferentes níveis de detalhamento."""
    print_header("DEMONSTRAÇÃO: DIFERENTES NÍVEIS DE DETALHAMENTO")
    
    analisador = AnalisadorCodigo()
    
    codigo_complexo = """
def funcao_complexa(dados):
    resultado = []
    for item in dados:
        if item > 0:
            for i in range(item):
                if i % 2 == 0:
                    resultado.append(i * 2)
                else:
                    resultado.append(i * 3)
    return resultado

def processar_dados(lista_dados):
    resultados_finais = []
    for dados in lista_dados:
        resultado = funcao_complexa(dados)
        resultados_finais.extend(resultado)
    return resultados_finais
"""
    
    print("📝 Código complexo para análise:")
    print(codigo_complexo[:200] + "..." if len(codigo_complexo) > 200 else codigo_complexo)
    
    niveis = [
        (NivelDetalhamento.BASICO, "Básico"),
        (NivelDetalhamento.INTERMEDIARIO, "Intermediário"),
        (NivelDetalhamento.AVANCADO, "Avançado")
    ]
    
    for nivel, nome in niveis:
        print(f"\n🔍 Análise {nome}...")
        
        try:
            inicio = datetime.now()
            sugestoes = await analisador.analisar_codigo(codigo_complexo, nivel)
            fim = datetime.now()
            
            tempo = (fim - inicio).total_seconds()
            pontuacao = analisador.calcular_pontuacao_qualidade(codigo_complexo)
            
            print(f"   ⏱️  Tempo: {tempo:.2f}s")
            print(f"   📊 Pontuação: {pontuacao:.1f}/100")
            print(f"   📋 Sugestões: {len(sugestoes)}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")

async def demonstrar_tipos_problemas():
    """Demonstra detecção de diferentes tipos de problemas."""
    print_header("DEMONSTRAÇÃO: DETECÇÃO DE DIFERENTES TIPOS DE PROBLEMAS")
    
    analisador = AnalisadorCodigo()
    
    exemplos = [
        ("Performance", """
def buscar_item(lista, item):
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1
"""),
        ("Legibilidade", """
def f(x,y):
    a=x+y
    if a>10:return a*2
    else:return a
"""),
        ("Boas Práticas", """
def dividir(a, b):
    try:
        return a / b
    except:
        pass
"""),
        ("Segurança", """
import os
user_input = input("Digite: ")
eval(user_input)
""")
    ]
    
    for categoria, codigo in exemplos:
        print(f"\n🔍 Analisando problemas de {categoria}:")
        print(f"📝 Código: {codigo.strip()[:100]}...")
        
        try:
            sugestoes = await analisador.analisar_codigo(
                codigo,
                nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO
            )
            
            pontuacao = analisador.calcular_pontuacao_qualidade(codigo)
            
            print(f"   📊 Pontuação: {pontuacao:.1f}/100")
            print(f"   📋 Sugestões: {len(sugestoes)}")
            
            # Mostra a primeira sugestão se houver
            if sugestoes:
                primeira = sugestoes[0]
                print(f"   💡 Primeira sugestão: {primeira.titulo}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def demonstrar_pontuacao():
    """Demonstra sistema de pontuação."""
    print_header("DEMONSTRAÇÃO: SISTEMA DE PONTUAÇÃO DE QUALIDADE")
    
    analisador = AnalisadorCodigo()
    
    exemplos = [
        ("Código Excelente", '''
def calcular_media(numeros: list[float]) -> float:
    """
    Calcula a média aritmética de uma lista de números.
    
    Args:
        numeros: Lista de números para calcular a média
        
    Returns:
        A média aritmética dos números
        
    Raises:
        ValueError: Se a lista estiver vazia
    """
    if not numeros:
        raise ValueError("Lista não pode estar vazia")
    
    return sum(numeros) / len(numeros)
'''),
        ("Código Bom", '''
def calcular_media(numeros):
    """Calcula a média de uma lista."""
    if not numeros:
        return 0
    return sum(numeros) / len(numeros)
'''),
        ("Código Razoável", '''
def calcular_media(numeros):
    soma = 0
    for num in numeros:
        soma += num
    return soma / len(numeros)
'''),
        ("Código Problemático", '''
def f(x):
    s=0
    for i in range(len(x)):s+=x[i]
    return s/len(x) if len(x)>0 else 0
''')
    ]
    
    for categoria, codigo in exemplos:
        pontuacao = analisador.calcular_pontuacao_qualidade(codigo)
        
        # Determina emoji baseado na pontuação
        if pontuacao >= 90:
            emoji = "🟢"
        elif pontuacao >= 80:
            emoji = "🟡"
        elif pontuacao >= 70:
            emoji = "🟠"
        else:
            emoji = "🔴"
        
        print(f"\n{emoji} {categoria}: {pontuacao:.1f}/100")

async def main():
    """Função principal da demonstração."""
    print("🤖 AGENTE DE OTIMIZAÇÃO DE CÓDIGO PYTHON")
    print("   Demonstração das Funcionalidades Principais")
    print("   " + "="*50)
    
    try:
        # Demonstrações
        await demonstrar_analise_basica()
        await demonstrar_diferentes_niveis()
        await demonstrar_tipos_problemas()
        demonstrar_pontuacao()
        
        print_header("DEMONSTRAÇÃO CONCLUÍDA")
        print("✅ Todas as funcionalidades principais foram demonstradas!")
        print("📚 Para mais informações, consulte o README.md")
        print("🔧 Para usar a API, execute: uvicorn main:app --reload")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante demonstração: {e}")
        print("🔧 Verifique se todas as dependências estão instaladas")

if __name__ == "__main__":
    asyncio.run(main())

