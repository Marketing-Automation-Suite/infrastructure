"""
Tests for service connectors
"""

import pytest
from src.connectors.base_connector import BaseConnector
from src.connectors.sendgrid_connector import SendGridConnector


def test_base_connector_interface():
    """Test that BaseConnector defines required methods"""
    # BaseConnector is abstract, so we test via a concrete implementation
    connector = SendGridConnector("sendgrid", "SendGrid")
    
    # Test that required methods exist
    assert hasattr(connector, "test_connection")
    assert hasattr(connector, "get_capabilities")
    assert hasattr(connector, "execute_action")
    assert hasattr(connector, "validate_credentials")


def test_validate_credentials():
    """Test credential validation"""
    connector = SendGridConnector("sendgrid", "SendGrid")
    
    # Valid credentials
    valid_creds = {"api_key": "test_key"}
    is_valid, error = connector.validate_credentials(valid_creds, ["api_key"])
    assert is_valid is True
    assert error is None
    
    # Missing required field
    invalid_creds = {}
    is_valid, error = connector.validate_credentials(invalid_creds, ["api_key"])
    assert is_valid is False
    assert "api_key" in error


def test_get_capabilities():
    """Test that connectors return capabilities"""
    connector = SendGridConnector("sendgrid", "SendGrid")
    capabilities = connector.get_capabilities()
    
    assert isinstance(capabilities, list)
    assert len(capabilities) > 0
    assert "send_email" in capabilities


def test_get_service_info():
    """Test getting service information"""
    connector = SendGridConnector("sendgrid", "SendGrid")
    info = connector.get_service_info()
    
    assert info["service_id"] == "sendgrid"
    assert info["service_name"] == "SendGrid"
    assert "capabilities" in info

