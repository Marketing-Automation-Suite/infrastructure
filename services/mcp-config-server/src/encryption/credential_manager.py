"""
Credential encryption and decryption using Fernet
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages encryption and decryption of service credentials"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize credential manager.
        
        Args:
            encryption_key: Master encryption key. If not provided, will be generated
                          or loaded from ENCRYPTION_KEY environment variable.
        """
        if encryption_key:
            self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        else:
            self.key = self._get_or_create_key()
        
        # Ensure key is 32 bytes for Fernet
        if len(self.key) != 44:  # Fernet keys are base64-encoded, 44 chars
            self.key = self._derive_key(self.key)
        
        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher: {str(e)}")
            raise ValueError("Invalid encryption key format")
    
    def _get_or_create_key(self) -> bytes:
        """
        Get encryption key from environment or generate a new one.
        
        Returns:
            Encryption key as bytes
        """
        key_str = os.getenv("ENCRYPTION_KEY")
        
        if key_str:
            # Key provided as base64 string
            try:
                return key_str.encode()
            except Exception:
                # If not base64, derive a key from it
                return self._derive_key(key_str.encode())
        else:
            # Generate a new key (for development only - should be set in production)
            logger.warning("ENCRYPTION_KEY not set. Generating new key (not recommended for production)")
            key = Fernet.generate_key()
            logger.warning(f"Generated encryption key: {key.decode()}")
            logger.warning("Set ENCRYPTION_KEY environment variable to use this key")
            return key
    
    def _derive_key(self, password: bytes) -> bytes:
        """
        Derive a Fernet key from a password using PBKDF2.
        
        Args:
            password: Password bytes
            
        Returns:
            Fernet-compatible key
        """
        # Use a fixed salt for consistency (in production, store salt separately)
        salt = b'mcp_config_server_salt_v1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> bytes:
        """
        Encrypt credentials dictionary.
        
        Args:
            credentials: Dictionary of credentials to encrypt
            
        Returns:
            Encrypted bytes
        """
        try:
            # Convert credentials to JSON string
            credentials_json = json.dumps(credentials)
            credentials_bytes = credentials_json.encode('utf-8')
            
            # Encrypt
            encrypted = self.cipher.encrypt(credentials_bytes)
            
            return encrypted
        except Exception as e:
            logger.error(f"Error encrypting credentials: {str(e)}")
            raise ValueError(f"Failed to encrypt credentials: {str(e)}")
    
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt credentials bytes to dictionary.
        
        Args:
            encrypted_data: Encrypted credentials bytes
            
        Returns:
            Decrypted credentials dictionary
        """
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_data)
            
            # Convert back to dictionary
            credentials_json = decrypted_bytes.decode('utf-8')
            credentials = json.loads(credentials_json)
            
            return credentials
        except Exception as e:
            logger.error(f"Error decrypting credentials: {str(e)}")
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string and return base64-encoded result.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt_credentials({"value": plaintext})
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, encrypted_b64: str) -> str:
        """
        Decrypt a base64-encoded encrypted string.
        
        Args:
            encrypted_b64: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        encrypted = base64.b64decode(encrypted_b64.encode('utf-8'))
        credentials = self.decrypt_credentials(encrypted)
        return credentials.get("value", "")


# Global instance
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """
    Get or create global credential manager instance.
    
    Returns:
        CredentialManager instance
    """
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager

