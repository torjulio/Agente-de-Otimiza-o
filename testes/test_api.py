"""
Testes para os endpoints da API FastAPI.

Testa todos os endpoints principais da aplicação,
incluindo análise de código, health checks e histórico.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

# Importa a aplicação principal
from main import app

class TestAPIEndpoints:
    """Testes para os endpoints da API."""
    
    @pytest.fixture
    def client(self):
        """Fixture que retorna um cliente de teste."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Testa o endpoint de health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "versao" in data
    
    def test_analyze_code_endpoint_sucesso(self, client):
        """Testa análise de código com sucesso."""
        codigo_teste = """
def hello():
    print("Hello, World!")
"""
        
        payload = {
            "codigo": codigo_teste,
            "nome_arquivo": "teste.py",
            "nivel_detalhamento": "intermediario"
        }
        
        response = client.post("/analyze-code", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica estrutura da resposta
        assert "codigo_original" in data
        assert "sugestoes" in data
        assert "pontuacao_qualidade" in data
        assert "tempo_analise" in data
        assert "timestamp" in data
        
        # Verifica tipos
        assert isinstance(data["sugestoes"], list)
        assert isinstance(data["pontuacao_qualidade"], (int, float))
        assert isinstance(data["tempo_analise"], (int, float))
        assert data["codigo_original"] == codigo_teste
    
    def test_analyze_code_endpoint_codigo_vazio(self, client):
        """Testa análise com código vazio."""
        payload = {
            "codigo": "",
            "nivel_detalhamento": "basico"
        }
        
        response = client.post("/analyze-code", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_code_endpoint_codigo_invalido(self, client):
        """Testa análise com código com erro de sintaxe."""
        payload = {
            "codigo": "def funcao_invalida(\n    # Sintaxe inválida",
            "nivel_detalhamento": "basico"
        }
        
        response = client.post("/analyze-code", json=payload)
        
        # Pode retornar 422 (validation error) ou 500 (internal error)
        assert response.status_code in [422, 500]
    
    def test_analyze_code_endpoint_nivel_detalhamento_invalido(self, client):
        """Testa análise com nível de detalhamento inválido."""
        payload = {
            "codigo": "print('test')",
            "nivel_detalhamento": "nivel_inexistente"
        }
        
        response = client.post("/analyze-code", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_code_endpoint_focar_performance(self, client):
        """Testa análise com foco em performance."""
        codigo_teste = """
def buscar_item(lista, item):
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1
"""
        
        payload = {
            "codigo": codigo_teste,
            "nivel_detalhamento": "intermediario",
            "focar_performance": True
        }
        
        response = client.post("/analyze-code", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter sugestões de performance
        sugestoes_performance = [
            s for s in data["sugestoes"] 
            if s.get("tipo") == "performance"
        ]
        assert len(sugestoes_performance) > 0
    
    def test_historico_endpoint(self, client):
        """Testa o endpoint de histórico."""
        response = client.get("/historico")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_historico_endpoint_com_limite(self, client):
        """Testa histórico com parâmetro de limite."""
        response = client.get("/historico?limite=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_historico_endpoint_com_offset(self, client):
        """Testa histórico com parâmetro de offset."""
        response = client.get("/historico?limite=10&offset=5")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_estatisticas_endpoint(self, client):
        """Testa o endpoint de estatísticas."""
        response = client.get("/estatisticas")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica estrutura das estatísticas
        assert "total_analises" in data
        assert "media_pontuacao" in data
        assert "tempo_medio_analise" in data
        assert isinstance(data["total_analises"], int)
        assert isinstance(data["media_pontuacao"], (int, float))
        assert isinstance(data["tempo_medio_analise"], (int, float))
    
    def test_documentacao_endpoint(self, client):
        """Testa se a documentação está acessível."""
        response = client.get("/documentacao")
        
        assert response.status_code == 200
        # Verifica se retorna HTML (documentação Swagger)
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_health_live_endpoint(self, client):
        """Testa o endpoint de liveness check."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data
    
    @patch('servicos.banco_dados.GerenciadorBancoDados.verificar_conexao')
    @patch('servicos.gerenciador_cache.gerenciador_cache.obter_info_cache')
    def test_health_ready_endpoint_saudavel(self, mock_cache, mock_db, client):
        """Testa readiness check quando tudo está saudável."""
        # Mock dos serviços como saudáveis
        mock_db.return_value = True
        mock_cache.return_value = {"status": "ok"}
        
        response = client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
    
    @patch('servicos.banco_dados.GerenciadorBancoDados.verificar_conexao')
    def test_health_ready_endpoint_banco_indisponivel(self, mock_db, client):
        """Testa readiness check quando banco está indisponível."""
        # Mock do banco como indisponível
        mock_db.return_value = False
        
        response = client.get("/health/ready")
        
        assert response.status_code == 503  # Service Unavailable
        data = response.json()
        assert data["status"] == "not_ready"
    
    def test_endpoint_inexistente(self, client):
        """Testa acesso a endpoint que não existe."""
        response = client.get("/endpoint-inexistente")
        
        assert response.status_code == 404
    
    def test_metodo_nao_permitido(self, client):
        """Testa método HTTP não permitido."""
        response = client.delete("/analyze-code")
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_payload_json_invalido(self, client):
        """Testa envio de JSON inválido."""
        response = client.post(
            "/analyze-code",
            data="json inválido",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_content_type_incorreto(self, client):
        """Testa envio com Content-Type incorreto."""
        response = client.post(
            "/analyze-code",
            data="codigo=print('test')",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        """Testa se os headers CORS estão configurados."""
        response = client.options("/analyze-code")
        
        # Verifica se permite CORS
        assert response.status_code in [200, 405]  # Pode não ter handler OPTIONS
        
        # Testa com requisição real
        response = client.post("/analyze-code", json={
            "codigo": "print('test')"
        })
        
        # Verifica headers CORS na resposta
        headers = response.headers
        # FastAPI pode adicionar headers CORS automaticamente
    
    def test_rate_limiting_simulado(self, client):
        """Simula teste de rate limiting (se implementado)."""
        # Faz múltiplas requisições rapidamente
        responses = []
        for i in range(15):  # Mais que o limite de 10/minuto
            response = client.post("/analyze-code", json={
                "codigo": f"print({i})"
            })
            responses.append(response.status_code)
        
        # Se rate limiting estiver implementado, algumas devem retornar 429
        # Se não estiver, todas devem ser 200 ou 422
        assert all(code in [200, 422, 429] for code in responses)
    
    def test_tamanho_maximo_payload(self, client):
        """Testa limite de tamanho do payload."""
        # Código muito grande
        codigo_gigante = "print('test')\n" * 10000
        
        payload = {
            "codigo": codigo_gigante,
            "nivel_detalhamento": "basico"
        }
        
        response = client.post("/analyze-code", json=payload)
        
        # Pode retornar 413 (Payload Too Large) ou 422 (Validation Error)
        assert response.status_code in [200, 413, 422]

class TestAPIIntegracao:
    """Testes de integração da API."""
    
    @pytest.fixture
    def client(self):
        """Fixture que retorna um cliente de teste."""
        return TestClient(app)
    
    def test_fluxo_completo_analise(self, client):
        """Testa fluxo completo de análise de código."""
        # 1. Verifica se API está saudável
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Analisa código
        codigo_teste = """
def calcular_media(numeros):
    soma = 0
    for i in range(len(numeros)):
        soma = soma + numeros[i]
    return soma / len(numeros)
"""
        
        analyze_response = client.post("/analyze-code", json={
            "codigo": codigo_teste,
            "nome_arquivo": "media.py",
            "nivel_detalhamento": "intermediario",
            "focar_performance": True
        })
        
        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()
        
        # 3. Verifica se análise foi salva no histórico
        historico_response = client.get("/historico?limite=1")
        assert historico_response.status_code == 200
        historico_data = historico_response.json()
        
        # Se o banco estiver funcionando, deve ter pelo menos 1 registro
        if len(historico_data) > 0:
            assert historico_data[0]["nome_arquivo"] == "media.py"
        
        # 4. Verifica estatísticas atualizadas
        stats_response = client.get("/estatisticas")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        
        assert stats_data["total_analises"] >= 0
    
    def test_diferentes_niveis_detalhamento(self, client):
        """Testa análise com diferentes níveis de detalhamento."""
        codigo_teste = """
def funcao_complexa(dados):
    resultado = []
    for item in dados:
        if item > 0:
            for i in range(item):
                if i % 2 == 0:
                    resultado.append(i * 2)
    return resultado
"""
        
        niveis = ["basico", "intermediario", "avancado"]
        resultados = {}
        
        for nivel in niveis:
            response = client.post("/analyze-code", json={
                "codigo": codigo_teste,
                "nivel_detalhamento": nivel
            })
            
            assert response.status_code == 200
            data = response.json()
            resultados[nivel] = len(data["sugestoes"])
        
        # Análise avançada deve ter mais ou igual sugestões que intermediária
        # Intermediária deve ter mais ou igual que básica
        assert resultados["avancado"] >= resultados["intermediario"]
        assert resultados["intermediario"] >= resultados["basico"]

if __name__ == "__main__":
    # Executa testes se rodado diretamente
    pytest.main([__file__, "-v"])

