"""
Tests for API authentication and authorization
"""

import pytest
import os
from fastapi.testclient import TestClient
from src.server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def api_key():
    """Test API key"""
    return "test-api-key-12345"


@pytest.fixture
def set_api_key(api_key, monkeypatch):
    """Set API key in environment"""
    monkeypatch.setenv("API_KEY", api_key)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DISABLE_AUTH", "false")
    return api_key


@pytest.fixture
def disable_auth(monkeypatch):
    """Disable authentication for testing"""
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("ENVIRONMENT", "development")


class TestAuthentication:
    """Test authentication middleware"""
    
    def test_marketplace_without_api_key_fails(self, client, set_api_key):
        """Test that marketplace endpoint requires API key"""
        response = client.get("/mcp/marketplace")
        assert response.status_code == 403
        assert "API key" in response.json()["detail"].lower()
    
    def test_marketplace_with_valid_api_key_succeeds(self, client, set_api_key):
        """Test that marketplace endpoint works with valid API key"""
        response = client.get(
            "/mcp/marketplace",
            headers={"X-API-Key": set_api_key}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_marketplace_with_invalid_api_key_fails(self, client, set_api_key):
        """Test that marketplace endpoint rejects invalid API key"""
        response = client.get(
            "/mcp/marketplace",
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 403
        assert "Invalid" in response.json()["detail"] or "missing" in response.json()["detail"].lower()
    
    def test_configure_service_without_api_key_fails(self, client, set_api_key):
        """Test that configure service endpoint requires API key"""
        response = client.post(
            "/mcp/tools/configure_service",
            json={
                "service_name": "sendgrid",
                "credentials": {"api_key": "test"},
                "config_name": "test"
            }
        )
        assert response.status_code == 403
    
    def test_configure_service_with_valid_api_key_succeeds(self, client, set_api_key):
        """Test that configure service endpoint works with valid API key"""
        # Note: This may fail if service not in registry, but auth should pass
        response = client.post(
            "/mcp/tools/configure_service",
            headers={"X-API-Key": set_api_key},
            json={
                "service_name": "sendgrid",
                "credentials": {"api_key": "test"},
                "config_name": "test"
            }
        )
        # Should not be 403 (auth error), might be 404 (service not found) or 500 (other error)
        assert response.status_code != 403
    
    def test_all_endpoints_require_auth(self, client, set_api_key):
        """Test that all protected endpoints require authentication"""
        endpoints = [
            ("GET", "/mcp/marketplace"),
            ("GET", "/mcp/tools/discover_services"),
            ("GET", "/mcp/tools/get_service_info?service_name=test"),
            ("GET", "/mcp/tools/list_configured_services"),
            ("GET", "/mcp/tools/get_configuration_guide?service_name=test"),
            ("GET", "/mcp/tools/search_marketplace"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            assert response.status_code == 403, f"{method} {endpoint} should require auth"
    
    def test_health_endpoints_public(self, client, set_api_key):
        """Test that health endpoints are public (no auth required)"""
        health_endpoints = [
            "/health",
            "/health/ready",
            "/health/live"
        ]
        
        for endpoint in health_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{endpoint} should be public"
            assert "status" in response.json()
    
    def test_disable_auth_flag(self, client, disable_auth):
        """Test that DISABLE_AUTH flag allows unauthenticated access"""
        response = client.get("/mcp/marketplace")
        # Should succeed when auth is disabled
        assert response.status_code in [200, 500]  # 500 if service not configured, but not 403
    
    def test_production_requires_api_key(self, client, monkeypatch):
        """Test that production mode requires API_KEY to be set"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DISABLE_AUTH", "false")
        monkeypatch.delenv("API_KEY", raising=False)
        
        # Should fail with 500 (server misconfiguration)
        response = client.get("/mcp/marketplace")
        assert response.status_code == 500
        assert "API_KEY not configured" in response.json()["detail"]
    
    def test_development_allows_no_key(self, client, monkeypatch):
        """Test that development mode allows requests without key"""
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("DISABLE_AUTH", "false")
        monkeypatch.delenv("API_KEY", raising=False)
        
        # Should allow (with warning logged)
        response = client.get("/mcp/marketplace")
        # Should not be 403, might be 200 or 500 depending on service config
        assert response.status_code != 403

