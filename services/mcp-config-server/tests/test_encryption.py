"""
Tests for credential encryption/decryption
"""

import pytest
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

