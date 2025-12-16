"""
Caching layer for token verifications
"""

import redis
import json
from typing import Optional, Dict
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache TTL (5 minutes)
CACHE_TTL = 300


class TokenCache:
    """Redis-based cache for token verifications"""
    
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache enabled")
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, network: str, contract: str, wallet: str, token_id: int) -> str:
        """Generate cache key"""
        return f"token_verify:{network}:{contract}:{wallet}:{token_id}"
    
    def get(self, network: str, contract: str, wallet: str, token_id: int) -> Optional[Dict]:
        """Get cached verification result"""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(network, contract, wallet, token_id)
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
        
        return None
    
    def set(self, network: str, contract: str, wallet: str, token_id: int, data: Dict):
        """Cache verification result"""
        if not self.enabled:
            return
        
        try:
            key = self._make_key(network, contract, wallet, token_id)
            self.redis_client.setex(
                key,
                CACHE_TTL,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
    
    def invalidate(self, network: str, contract: str, wallet: str, token_id: int):
        """Invalidate cache entry"""
        if not self.enabled:
            return
        
        try:
            key = self._make_key(network, contract, wallet, token_id)
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")


# Global cache instance
token_cache = TokenCache()

