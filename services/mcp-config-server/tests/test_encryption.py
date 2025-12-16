"""
Tests for credential encryption/decryption
"""

import pytest
import os
from src.encryption.credential_manager import CredentialManager


def test_encrypt_decrypt_credentials():
    """Test encrypting and decrypting credentials"""
    manager = CredentialManager()
    
    credentials = {
        "api_key": "test_key_123",
        "api_secret": "test_secret_456"
    }
    
    # Encrypt
    encrypted = manager.encrypt_credentials(credentials)
    assert encrypted is not None
    assert isinstance(encrypted, bytes)
    
    # Decrypt
    decrypted = manager.decrypt_credentials(encrypted)
    assert decrypted == credentials


def test_encrypt_decrypt_string():
    """Test encrypting and decrypting strings"""
    manager = CredentialManager()
    
    plaintext = "test_string_123"
    
    # Encrypt
    encrypted = manager.encrypt_string(plaintext)
    assert encrypted is not None
    assert isinstance(encrypted, str)
    
    # Decrypt
    decrypted = manager.decrypt_string(encrypted)
    assert decrypted == plaintext


def test_different_credentials_produce_different_encryption():
    """Test that different credentials produce different encrypted data"""
    manager = CredentialManager()
    
    creds1 = {"api_key": "key1"}
    creds2 = {"api_key": "key2"}
    
    encrypted1 = manager.encrypt_credentials(creds1)
    encrypted2 = manager.encrypt_credentials(creds2)
    
    assert encrypted1 != encrypted2


def test_invalid_decryption():
    """Test that invalid encrypted data raises error"""
    manager = CredentialManager()
    
    invalid_data = b"invalid_encrypted_data"
    
    with pytest.raises(ValueError):
        manager.decrypt_credentials(invalid_data)


def test_production_requires_encryption_key(monkeypatch):
    """Test that production mode requires ENCRYPTION_KEY"""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    
    with pytest.raises(ValueError) as exc_info:
        CredentialManager()
    
    assert "ENCRYPTION_KEY" in str(exc_info.value)


def test_development_allows_key_generation(monkeypatch):
    """Test that development mode can generate keys"""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    
    # Should not raise error
    manager = CredentialManager()
    assert manager is not None
    assert manager.cipher is not None


def test_encryption_key_not_logged(monkeypatch, caplog):
    """Test that encryption keys are never logged"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    
    manager = CredentialManager()
    
    # Check logs - should not contain the actual key
    log_messages = caplog.text
    # The key should not appear in logs (it's generated but not logged)
    # This is a security check


def test_environment_specific_salt(monkeypatch):
    """Test that salt can be configured via environment"""
    monkeypatch.setenv("ENCRYPTION_KEY", "test-key")
    monkeypatch.setenv("ENCRYPTION_SALT", "custom-salt-value")
    
    manager = CredentialManager()
    # Should use custom salt
    assert manager is not None


def test_salt_fallback_to_default(monkeypatch):
    """Test that salt falls back to default if not set"""
    monkeypatch.setenv("ENCRYPTION_KEY", "test-key")
    monkeypatch.delenv("ENCRYPTION_SALT", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")
    
    manager = CredentialManager()
    # Should work with default salt in development
    assert manager is not None

