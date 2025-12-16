-- MCP Configuration Server Database Schema

-- Service Registry: Available services in marketplace
CREATE TABLE IF NOT EXISTS service_registry (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    definition_path VARCHAR(500),
    connector_class VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Configurations: Encrypted user configurations
CREATE TABLE IF NOT EXISTS service_configurations (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(255) NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    encrypted_credentials BYTEA NOT NULL,
    settings JSONB,
    status VARCHAR(50) DEFAULT 'pending', -- pending, active, failed, disabled
    last_tested_at TIMESTAMP,
    last_test_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, config_name)
);

-- Service Connectors: Plugin metadata
CREATE TABLE IF NOT EXISTS service_connectors (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(255) NOT NULL REFERENCES service_registry(id) ON DELETE CASCADE,
    connector_class VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    capabilities JSONB,
    is_loaded BOOLEAN DEFAULT false,
    loaded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Connection Tests: Test history
CREATE TABLE IF NOT EXISTS connection_tests (
    id SERIAL PRIMARY KEY,
    configuration_id INTEGER NOT NULL REFERENCES service_configurations(id) ON DELETE CASCADE,
    test_status VARCHAR(50) NOT NULL, -- success, failed, timeout
    test_result JSONB,
    error_message TEXT,
    test_duration_ms INTEGER,
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_service_registry_category ON service_registry(category);
CREATE INDEX IF NOT EXISTS idx_service_registry_active ON service_registry(is_active);
CREATE INDEX IF NOT EXISTS idx_service_configurations_service_id ON service_configurations(service_id);
CREATE INDEX IF NOT EXISTS idx_service_configurations_status ON service_configurations(status);
CREATE INDEX IF NOT EXISTS idx_connection_tests_configuration_id ON connection_tests(configuration_id);
CREATE INDEX IF NOT EXISTS idx_connection_tests_tested_at ON connection_tests(tested_at);

