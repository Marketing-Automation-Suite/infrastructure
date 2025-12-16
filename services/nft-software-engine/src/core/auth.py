"""
Authentication integration for NFT Software Engine
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
import httpx

from ..config.settings import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token from auth service"""
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        return {"user_id": user_id, "payload": payload}
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


async def verify_external_token(token: str, service_url: str = None) -> Optional[Dict[str, Any]]:
    """Verify token with external auth service"""
    if not service_url:
        service_url = settings.AUTH_SERVICE_URL
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{service_url}/verify",
                headers={"Authorization": f"Bearer {token}"},
                json={"service": "nft-software-engine"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"External auth verification failed: {response.status_code}")
                return None
                
    except httpx.RequestError as e:
        logger.error(f"External auth service error: {e}")
        return None


def require_auth(func):
    """Decorator to require authentication for API endpoints"""
    async def wrapper(*args, **kwargs):
        # This would be used as a FastAPI dependency
        # Implementation would be completed in Phase 4
        return await func(*args, **kwargs)
    return wrapper


def create_access_token(data: dict, expires_hours: int = None) -> str:
    """Create JWT access token"""
    if expires_hours is None:
        expires_hours = settings.JWT_EXPIRATION_HOURS
    
    to_encode = data.copy()
    from datetime import datetime, timedelta
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


async def get_current_user(token: str = None) -> Optional[Dict[str, Any]]:
    """Get current user from token"""
    if not token:
        return None
        
    # Try local verification first
    user_data = await verify_token(token)
    if user_data:
        return user_data
    
    # Try external verification
    user_data = await verify_external_token(token)
    if user_data:
        return user_data
    
    return None


def require_admin():
    """Admin role requirement for API endpoints"""
    # Implementation would check for admin role
    # Completed in Phase 4
    pass


def check_tier_access(user_tier: str, required_tier: str) -> bool:
    """Check if user tier has access to required tier"""
    tier_hierarchy = {
        "free": 0,
        "bronze": 1,
        "silver": 2,
        "gold": 3,
        "platinum": 4
    }
    
    user_level = tier_hierarchy.get(user_tier.lower(), -1)
    required_level = tier_hierarchy.get(required_tier.lower(), 999)
    
    return user_level >= required_level
