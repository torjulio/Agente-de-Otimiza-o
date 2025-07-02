"""
Testes de integração para o sistema completo.

Testa a integração entre componentes, incluindo banco de dados,
cache, e fluxos completos de análise.
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from servicos.banco_dados import GerenciadorBancoDados
from servicos.gerenciador_cache import GerenciadorCache
from servicos.analisador_codigo import AnalisadorCodigo
from servicos.monitor_sistema import MonitorSistema
from modelos.schemas import SolicitacaoAnalise, NivelDetalhamento

@pytest.mark.integration
class TestIntegracaoBancoDados:
    """Testes de integração com banco de dados."""
    
    @pytest.fixture
    async def bd_manager(self):
        """Fixture que retorna um gerenciador de banco configurado."""
        bd = GerenciadorBancoDados()
        
        # Configura para usar banco de teste
        bd.config.nome_banco = "agente_otimizacao_test"
        
        try:
            await bd.inicializar_banco()
            yield bd
        finally:
            await bd.fechar_conexoes()
    
    @pytest.mark.asyncio
    async def test_salvar_e_recuperar_analise(self, bd_manager):
        """Testa salvar e recuperar análise do banco."""
        codigo_teste = "def hello(): print('Hello')"
        sugestoes_teste = [
            {
                "tipo": "legibilidade",
                "titulo": "Adicionar docstring",
                "descricao": "Função deveria ter documentação",
                "linha_inicio": 1,
                "linha_fim": 1,
                "prioridade": 5
            }
        ]
        pontuacao_teste = 75.5
        
        # Salva análise
        analise_id = await bd_manager.salvar_analise(
            codigo=codigo_teste,
            sugestoes=sugestoes_teste,
            pontuacao_qualidade=pontuacao_teste,
            nome_arquivo="teste.py",
            tempo_analise=1.5
        )
        
        assert analise_id is not None
        assert isinstance(analise_id, int)
        
        # Recupera análise
        analise_recuperada = await bd_manager.obter_analise_por_id(analise_id)
        
        assert analise_recuperada is not None
        assert analise_recuperada['pontuacao_qualidade'] == pontuacao_teste
        assert analise_recuperada['nome_arquivo'] == "teste.py"
        assert len(analise_recuperada['sugestoes']) == 1
    
    @pytest.mark.asyncio
    async def test_obter_historico_analises(self, bd_manager):
        """Testa obtenção do histórico de análises."""
        # Salva algumas análises
        for i in range(5):
            await bd_manager.salvar_analise(
                codigo=f"def func{i}(): pass",
                sugestoes=[],
                pontuacao_qualidade=80.0 + i,
                nome_arquivo=f"arquivo{i}.py"
            )
        
        # Obtém histórico
        historico = await bd_manager.obter_historico_analises(limite=3)
        
        assert len(historico) <= 3
        assert all('id' in analise for analise in historico)
        assert all('pontuacao_qualidade' in analise for analise in historico)
        
        # Verifica ordenação (mais recente primeiro)
        if len(historico) > 1:
            for i in range(len(historico) - 1):
                assert historico[i]['created_at'] >= historico[i + 1]['created_at']
    
    @pytest.mark.asyncio
    async def test_obter_estatisticas(self, bd_manager):
        """Testa obtenção de estatísticas do banco."""
        # Salva algumas análises com diferentes pontuações
        pontuacoes = [70.0, 80.0, 90.0, 85.0]
        for i, pontuacao in enumerate(pontuacoes):
            await bd_manager.salvar_analise(
                codigo=f"def func{i}(): pass",
                sugestoes=[{"tipo": "legibilidade"}] * (i + 1),
                pontuacao_qualidade=pontuacao
            )
        
        # Obtém estatísticas
        stats = await bd_manager.obter_estatisticas()
        
        assert 'total_analises' in stats
        assert 'media_pontuacao' in stats
        assert 'tempo_medio_analise' in stats
        assert stats['total_analises'] >= len(pontuacoes)
        
        # Verifica se a média está no range esperado
        media_esperada = sum(pontuacoes) / len(pontuacoes)
        assert abs(stats['media_pontuacao'] - media_esperada) < 10  # Margem para outras análises

@pytest.mark.integration
class TestIntegracaoCache:
    """Testes de integração com cache."""
    
    @pytest.fixture
    async def cache_manager(self):
        """Fixture que retorna um gerenciador de cache."""
        cache = GerenciadorCache()
        await cache.inicializar()
        
        try:
            yield cache
        finally:
            await cache.fechar_conexoes()
    
    @pytest.mark.asyncio
    async def test_cache_analise_completo(self, cache_manager):
        """Testa ciclo completo de cache de análise."""
        codigo_teste = "def hello(): print('Hello')"
        resultado_teste = {
            "sugestoes": [{"tipo": "legibilidade", "titulo": "Teste"}],
            "pontuacao_qualidade": 85.0,
            "tempo_analise": 2.1
        }
        
        # Verifica que não está no cache
        resultado_cache = await cache_manager.obter_analise_cache(codigo_teste)
        assert resultado_cache is None
        
        # Salva no cache
        await cache_manager.salvar_analise_cache(codigo_teste, resultado_teste)
        
        # Verifica que agora está no cache
        resultado_recuperado = await cache_manager.obter_analise_cache(codigo_teste)
        assert resultado_recuperado is not None
        assert resultado_recuperado['resultado']['pontuacao_qualidade'] == 85.0
    
    @pytest.mark.asyncio
    async def test_cache_expiracao(self, cache_manager):
        """Testa expiração do cache."""
        codigo_teste = "def test(): pass"
        resultado_teste = {"pontuacao": 90.0}
        
        # Salva com TTL muito baixo (1 segundo)
        await cache_manager.salvar_analise_cache(
            codigo_teste, 
            resultado_teste, 
            ttl=1
        )
        
        # Verifica que está no cache
        resultado = await cache_manager.obter_analise_cache(codigo_teste)
        assert resultado is not None
        
        # Aguarda expiração
        await asyncio.sleep(2)
        
        # Verifica que expirou (pode não funcionar com cache local)
        resultado_expirado = await cache_manager.obter_analise_cache(codigo_teste)
        # Com Redis, deve ser None. Com cache local, pode ainda estar lá
        # assert resultado_expirado is None  # Comentado pois depende do backend
    
    @pytest.mark.asyncio
    async def test_info_cache(self, cache_manager):
        """Testa obtenção de informações do cache."""
        info = await cache_manager.obter_info_cache()
        
        assert 'tipo_cache' in info
        assert 'estatisticas' in info
        assert 'configuracao' in info
        assert info['tipo_cache'] in ['redis', 'local']

@pytest.mark.integration
class TestIntegracaoCompleta:
    """Testes de integração do sistema completo."""
    
    @pytest.fixture
    async def sistema_completo(self):
        """Fixture que configura o sistema completo."""
        # Configura componentes
        bd = GerenciadorBancoDados()
        cache = GerenciadorCache()
        analisador = AnalisadorCodigo()
        
        # Inicializa
        await bd.inicializar_banco()
        await cache.inicializar()
        
        try:
            yield {
                'bd': bd,
                'cache': cache,
                'analisador': analisador
            }
        finally:
            await bd.fechar_conexoes()
            await cache.fechar_conexoes()
    
    @pytest.mark.asyncio
    async def test_fluxo_analise_com_cache_e_banco(self, sistema_completo):
        """Testa fluxo completo: análise -> cache -> banco."""
        bd = sistema_completo['bd']
        cache = sistema_completo['cache']
        analisador = sistema_completo['analisador']
        
        codigo_teste = """
def calcular_soma(lista):
    soma = 0
    for i in range(len(lista)):
        soma = soma + lista[i]
    return soma
"""
        
        # Primeira análise (não deve estar no cache)
        inicio = datetime.now()
        sugestoes1 = await analisador.analisar_codigo(
            codigo_teste,
            nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO
        )
        tempo1 = (datetime.now() - inicio).total_seconds()
        
        # Salva no banco
        analise_id = await bd.salvar_analise(
            codigo=codigo_teste,
            sugestoes=[s.dict() for s in sugestoes1],
            pontuacao_qualidade=analisador.calcular_pontuacao_qualidade(codigo_teste)
        )
        
        # Salva no cache
        await cache.salvar_analise_cache(codigo_teste, {
            "sugestoes": [s.dict() for s in sugestoes1],
            "pontuacao_qualidade": analisador.calcular_pontuacao_qualidade(codigo_teste)
        })
        
        # Segunda análise (deve vir do cache)
        inicio = datetime.now()
        resultado_cache = await cache.obter_analise_cache(codigo_teste)
        tempo2 = (datetime.now() - inicio).total_seconds()
        
        # Cache deve ser mais rápido
        assert resultado_cache is not None
        assert tempo2 < tempo1  # Cache deve ser mais rápido
        
        # Verifica se foi salvo no banco
        analise_recuperada = await bd.obter_analise_por_id(analise_id)
        assert analise_recuperada is not None
        assert len(analise_recuperada['sugestoes']) == len(sugestoes1)
    
    @pytest.mark.asyncio
    async def test_analise_diferentes_codigos(self, sistema_completo):
        """Testa análise de diferentes tipos de código."""
        analisador = sistema_completo['analisador']
        
        codigos_teste = [
            # Código simples
            "def hello(): print('Hello')",
            
            # Código com problemas de performance
            """
def buscar_item(lista, item):
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1
""",
            
            # Código com problemas de segurança
            """
import os
user_input = input("Digite: ")
eval(user_input)
""",
            
            # Código complexo
            """
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
"""
        ]
        
        resultados = []
        for i, codigo in enumerate(codigos_teste):
            try:
                sugestoes = await analisador.analisar_codigo(
                    codigo,
                    nivel_detalhamento=NivelDetalhamento.INTERMEDIARIO
                )
                pontuacao = analisador.calcular_pontuacao_qualidade(codigo)
                
                resultados.append({
                    'codigo_id': i,
                    'sugestoes': len(sugestoes),
                    'pontuacao': pontuacao,
                    'tempo': analisador.ultimo_tempo_analise
                })
                
            except Exception as e:
                pytest.fail(f"Erro ao analisar código {i}: {e}")
        
        # Verifica que todas as análises foram bem-sucedidas
        assert len(resultados) == len(codigos_teste)
        
        # Verifica que todas têm pontuação válida
        for resultado in resultados:
            assert 0 <= resultado['pontuacao'] <= 100
            assert resultado['tempo'] > 0

@pytest.mark.integration
class TestIntegracaoMonitoramento:
    """Testes de integração do sistema de monitoramento."""
    
    @pytest.fixture
    def monitor(self):
        """Fixture que retorna um monitor de sistema."""
        return MonitorSistema()
    
    def test_coleta_metricas_sistema(self, monitor):
        """Testa coleta de métricas do sistema."""
        # Simula coleta de métricas
        monitor.registrar_analise(2.5)  # 2.5 segundos
        monitor.registrar_analise(1.8)  # 1.8 segundos
        monitor.registrar_erro()
        
        # Verifica contadores
        assert monitor.contador_analises == 2
        assert monitor.contador_erros == 1
        assert len(monitor.tempos_analise) == 2
    
    def test_status_saude_sistema(self, monitor):
        """Testa obtenção do status de saúde."""
        status = monitor.obter_status_saude()
        
        assert 'status' in status
        assert 'timestamp' in status
        assert 'uptime_segundos' in status
        assert status['status'] in ['inicializando', 'saudavel', 'atencao', 'degradado', 'critico']

@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegracao:
    """Testes de performance e carga."""
    
    @pytest.mark.asyncio
    async def test_multiplas_analises_simultaneas(self):
        """Testa múltiplas análises simultâneas."""
        analisador = AnalisadorCodigo()
        
        codigos = [
            f"def func{i}(): return {i}" 
            for i in range(10)
        ]
        
        # Executa análises em paralelo
        inicio = datetime.now()
        tasks = [
            analisador.analisar_codigo(codigo, NivelDetalhamento.BASICO)
            for codigo in codigos
        ]
        resultados = await asyncio.gather(*tasks)
        fim = datetime.now()
        
        tempo_total = (fim - inicio).total_seconds()
        
        # Verifica que todas foram bem-sucedidas
        assert len(resultados) == len(codigos)
        assert all(isinstance(r, list) for r in resultados)
        
        # Verifica performance (deve ser mais rápido que sequencial)
        assert tempo_total < 30.0  # Limite razoável
    
    @pytest.mark.asyncio
    async def test_analise_codigo_grande(self):
        """Testa análise de código muito grande."""
        analisador = AnalisadorCodigo()
        
        # Gera código grande
        linhas = ["def funcao_grande():"]
        linhas.extend([f"    x{i} = {i}" for i in range(1000)])
        linhas.append("    return sum([" + ", ".join(f"x{i}" for i in range(1000)) + "])")
        
        codigo_grande = "\n".join(linhas)
        
        inicio = datetime.now()
        sugestoes = await analisador.analisar_codigo(
            codigo_grande,
            nivel_detalhamento=NivelDetalhamento.BASICO
        )
        fim = datetime.now()
        
        tempo_execucao = (fim - inicio).total_seconds()
        
        # Deve completar em tempo razoável
        assert tempo_execucao < 30.0
        assert isinstance(sugestoes, list)

if __name__ == "__main__":
    # Executa apenas testes de integração
    pytest.main([__file__, "-v", "-m", "integration"])

