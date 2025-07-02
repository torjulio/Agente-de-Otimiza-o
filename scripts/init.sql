-- Script de inicialização do banco de dados PostgreSQL
-- para o Agente de Otimização de Código

-- Configurações iniciais
SET timezone = 'UTC';

-- Criação de extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Comentários sobre o banco
COMMENT ON DATABASE agente_otimizacao IS 'Banco de dados para o Agente de Otimização de Código Python';

-- Função para logging automático
CREATE OR REPLACE FUNCTION log_mudanca()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs_auditoria (acao, detalhes, created_at)
    VALUES (
        TG_OP,
        jsonb_build_object(
            'tabela', TG_TABLE_NAME,
            'dados_antigos', CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
            'dados_novos', CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
        ),
        CURRENT_TIMESTAMP
    );
    
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

-- Dados iniciais para configurações
INSERT INTO configuracoes_sistema (chave, valor, descricao) VALUES
('versao_inicial', '{"versao": "1.0.0", "data_instalacao": "' || CURRENT_TIMESTAMP || '"}', 'Versão inicial do sistema'),
('manutencao', '{"ativo": false, "mensagem": "Sistema em operação normal"}', 'Status de manutenção do sistema'),
('limites_api', '{"requests_por_minuto": 100, "tamanho_max_codigo": 50000}', 'Limites da API')
ON CONFLICT (chave) DO NOTHING;

-- Criação de usuário específico para a aplicação (opcional)
-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'agente_app') THEN
--         CREATE ROLE agente_app WITH LOGIN PASSWORD 'senha_segura_aqui';
--         GRANT CONNECT ON DATABASE agente_otimizacao TO agente_app;
--         GRANT USAGE ON SCHEMA public TO agente_app;
--         GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO agente_app;
--         GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO agente_app;
--     END IF;
-- END
-- $$;

