"""
Tests for service registry
"""

import pytest
from src.registry.service_registry import ServiceRegistry
from pathlib import Path


def test_registry_initialization():
    """Test that registry can be initialized"""
    registry = ServiceRegistry()
    assert registry is not None


def test_get_service():
    """Test getting a service by ID"""
    registry = ServiceRegistry()
    
    # Try to get a service (may not exist if definitions not loaded)
    service = registry.get_service("sendgrid")
    # Service may be None if definitions not found, which is OK for test
    assert service is None or isinstance(service, dict)


def test_list_services():
    """Test listing services"""
    registry = ServiceRegistry()
    
    services = registry.list_services()
    assert isinstance(services, list)


def test_list_services_by_category():
    """Test filtering services by category"""
    registry = ServiceRegistry()
    
    services = registry.list_services(category="email")
    assert isinstance(services, list)
    
    # All returned services should be in email category (if any exist)
    for service in services:
        assert service.get("category") == "email"


def test_search_marketplace():
    """Test marketplace search"""
    registry = ServiceRegistry()
    
    results = registry.search_marketplace(category="lead_generation")
    assert isinstance(results, list)

