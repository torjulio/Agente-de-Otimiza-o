"""
Testes simples para validar a funcionalidade básica da API.

Foca nos endpoints principais e funcionalidades essenciais.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

class TestAPIBasica:
    """Testes básicos da API."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Testa endpoint de saúde."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_analyze_code_endpoint_basico(self, client):
        """Testa análise básica de código."""
        codigo_simples = "def hello(): print('Hello, World!')"
        
        response = client.post("/analyze-code", json={
            "codigo": codigo_simples,
            "nivel_detalhamento": "basico"
        })
        
        assert response.status_code == 200
        
        data = response.json()
        assert "codigo_original" in data
        assert "sugestoes" in data
        assert "pontuacao_qualidade" in data
        assert "tempo_analise" in data
        
        # Verifica tipos básicos
        assert isinstance(data["sugestoes"], list)
        assert isinstance(data["pontuacao_qualidade"], (int, float))
        assert data["codigo_original"] == codigo_simples
    
    def test_analyze_code_diferentes_niveis(self, client):
        """Testa diferentes níveis de detalhamento."""
        codigo = "def soma(a, b): return a + b"
        
        for nivel in ["basico", "intermediario", "avancado"]:
            response = client.post("/analyze-code", json={
                "codigo": codigo,
                "nivel_detalhamento": nivel
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "sugestoes" in data
    
    def test_analyze_code_com_nome_arquivo(self, client):
        """Testa análise com nome de arquivo."""
        response = client.post("/analyze-code", json={
            "codigo": "print('test')",
            "nome_arquivo": "teste.py",
            "nivel_detalhamento": "basico"
        })
        
        assert response.status_code == 200
    
    def test_analyze_code_focar_performance(self, client):
        """Testa análise com foco em performance."""
        codigo = """
def buscar(lista, item):
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1
"""
        
        response = client.post("/analyze-code", json={
            "codigo": codigo,
            "focar_performance": True,
            "nivel_detalhamento": "intermediario"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "sugestoes" in data
    
    def test_historico_endpoint(self, client):
        """Testa endpoint de histórico."""
        response = client.get("/historico")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_estatisticas_endpoint(self, client):
        """Testa endpoint de estatísticas."""
        response = client.get("/estatisticas")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_analises" in data
        assert isinstance(data["total_analises"], int)
    
    def test_documentacao_endpoint(self, client):
        """Testa se documentação está acessível."""
        response = client.get("/documentacao")
        assert response.status_code == 200
    
    def test_health_live_endpoint(self, client):
        """Testa liveness check."""
        response = client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
    
    def test_health_ready_endpoint(self, client):
        """Testa readiness check."""
        response = client.get("/health/ready")
        # Pode retornar 200 ou 503 dependendo do estado dos serviços
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data
    
    def test_codigo_vazio_retorna_erro(self, client):
        """Testa que código vazio retorna erro."""
        response = client.post("/analyze-code", json={
            "codigo": "",
            "nivel_detalhamento": "basico"
        })
        
        # Deve retornar erro de validação
        assert response.status_code == 422
    
    def test_nivel_detalhamento_invalido(self, client):
        """Testa nível de detalhamento inválido."""
        response = client.post("/analyze-code", json={
            "codigo": "print('test')",
            "nivel_detalhamento": "nivel_inexistente"
        })
        
        assert response.status_code == 422
    
    def test_payload_json_invalido(self, client):
        """Testa payload JSON inválido."""
        response = client.post(
            "/analyze-code",
            data="json inválido",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_endpoint_inexistente(self, client):
        """Testa endpoint que não existe."""
        response = client.get("/endpoint-que-nao-existe")
        assert response.status_code == 404
    
    def test_metodo_nao_permitido(self, client):
        """Testa método HTTP não permitido."""
        response = client.delete("/analyze-code")
        assert response.status_code == 405

class TestFluxoCompleto:
    """Testa fluxo completo de uso da API."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste."""
        return TestClient(app)
    
    def test_fluxo_analise_completa(self, client):
        """Testa fluxo completo de análise."""
        # 1. Verifica saúde da API
        health = client.get("/health")
        assert health.status_code == 200
        
        # 2. Analisa código
        codigo = """
def calcular_media(numeros):
    soma = 0
    for numero in numeros:
        soma += numero
    return soma / len(numeros)
"""
        
        response = client.post("/analyze-code", json={
            "codigo": codigo,
            "nome_arquivo": "media.py",
            "nivel_detalhamento": "intermediario"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica estrutura da resposta
        assert "codigo_original" in data
        assert "sugestoes" in data
        assert "pontuacao_qualidade" in data
        assert "tempo_analise" in data
        assert "timestamp" in data
        
        # 3. Verifica histórico (pode estar vazio se banco não estiver configurado)
        historico = client.get("/historico")
        assert historico.status_code == 200
        
        # 4. Verifica estatísticas
        stats = client.get("/estatisticas")
        assert stats.status_code == 200
        stats_data = stats.json()
        assert "total_analises" in stats_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

