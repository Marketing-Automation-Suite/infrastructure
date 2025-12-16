"""
Cryptographic utilities for NFT Software Engine
"""

import secrets
import hashlib
from typing import Dict, Any
from eth_account import Account
from eth_account.messages import encode_defunct


def generate_wallet() -> Dict[str, str]:
    """Generate a new Ethereum wallet"""
    account = Account.create()
    
    return {
        "address": account.address,
        "private_key": account.key.hex(),
        "public_key": account.address  # Use address as public key for simplicity
    }


def validate_signature(message: str, signature: str, address: str) -> bool:
    """Validate a signature against an address"""
    try:
        # Encode the message
        message_bytes = encode_defunct(text=message)
        
        # Recover the address from signature
        recovered_address = Account.recover_message(message_bytes, signature=signature)
        
        # Compare addresses
        return recovered_address.lower() == address.lower()
        
    except Exception:
        return False


def sign_message(message: str, private_key: str) -> str:
    """Sign a message with private key"""
    try:
        account = Account.from_key(private_key)
        message_bytes = encode_defunct(text=message)
        
        signed_message = account.sign_message(message_bytes)
        return signed_message.signature.hex()
        
    except Exception as e:
        raise ValueError(f"Failed to sign message: {e}")


def hash_data(data: str) -> str:
    """Hash data using SHA256"""
    return hashlib.sha256(data.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def validate_private_key(private_key: str) -> bool:
    """Validate if private key format is correct"""
    try:
        # Remove '0x' prefix if present
        key = private_key.replace('0x', '') if private_key.startswith('0x') else private_key
        
        # Check length (64 hex characters for private key)
        return len(key) == 64 and all(c in '0123456789abcdefABCDEF' for c in key)
        
    except Exception:
        return False


def derive_address_from_private_key(private_key: str) -> str:
    """Derive address from private key"""
    try:
        account = Account.from_key(private_key)
        return account.address
        
    except Exception as e:
        raise ValueError(f"Invalid private key: {e}")
