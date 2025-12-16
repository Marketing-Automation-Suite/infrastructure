"""
JWT token generation and validation
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
import os

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Password hashing - use pbkdf2_hmac directly to avoid passlib/bcrypt issues
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Format: salt:hash (both hex encoded)
        salt_hex, hash_hex = hashed_password.split(':')
        salt = bytes.fromhex(salt_hex)
        # Hash the provided password with the same salt
        new_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt, 100000)
        return new_hash.hex() == hash_hex
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2"""
    salt = secrets.token_bytes(16)
    hash_value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    # Return format: salt:hash (both hex encoded)
    return f"{salt.hex()}:{hash_value.hex()}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

