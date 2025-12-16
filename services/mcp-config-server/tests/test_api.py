"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_endpoint():
    """Test readiness endpoint"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_liveness_endpoint():
    """Test liveness endpoint"""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_marketplace_endpoint():
    """Test marketplace endpoint"""
    response = client.get("/mcp/marketplace")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_discover_services_endpoint():
    """Test discover services endpoint"""
    response = client.get("/mcp/tools/discover_services", params={"category": "all"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_get_service_info_endpoint():
    """Test get service info endpoint"""
    # Test with existing service
    response = client.get("/mcp/tools/get_service_info", params={"service_name": "sendgrid"})
    # May return 404 if service not in registry, or 200 if found
    assert response.status_code in [200, 404]
    
    # Test with non-existent service
    response = client.get("/mcp/tools/get_service_info", params={"service_name": "nonexistent"})
    assert response.status_code == 404


def test_get_configuration_guide_endpoint():
    """Test get configuration guide endpoint"""
    # Test with existing service
    response = client.get("/mcp/tools/get_configuration_guide", params={"service_name": "sendgrid"})
    # May return 404 if service not in registry, or 200 if found
    assert response.status_code in [200, 404]


def test_list_configured_services_endpoint():
    """Test list configured services endpoint"""
    response = client.get("/mcp/tools/list_configured_services")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

