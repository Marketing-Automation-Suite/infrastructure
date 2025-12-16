"""
Rate limiting utilities
"""

import redis
import os
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting based on user tier"""
    
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.enabled = True
            logger.info("Rate limiter enabled with Redis")
        except Exception as e:
            logger.warning(f"Redis not available, rate limiting disabled: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, user_id: str, limit_type: str) -> str:
        """Generate Redis key for rate limiting"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        return f"rate_limit:{user_id}:{limit_type}:{today}"
    
    def check_rate_limit(
        self,
        user_id: str,
        tier: str,
        limit_type: str = 'api_calls_per_day'
    ) -> tuple[bool, Optional[int]]:
        """
        Check if user has exceeded rate limit
        
        Args:
            user_id: User ID
            tier: User tier
            limit_type: Type of limit to check
            
        Returns:
            Tuple of (allowed, remaining_count)
        """
        if not self.enabled:
            return True, None
        
        from .tier_checker import tier_checker
        limits = tier_checker.get_tier_limits(tier)
        limit = limits.get(limit_type, 0)
        
        # -1 means unlimited
        if limit == -1:
            return True, None
        
        key = self._make_key(user_id, limit_type)
        
        try:
            current = self.redis_client.get(key)
            current_count = int(current) if current else 0
            
            if current_count >= limit:
                return False, 0
            
            # Increment counter
            self.redis_client.incr(key)
            # Set expiration to end of day
            self.redis_client.expire(key, 86400)  # 24 hours
            
            remaining = limit - current_count - 1
            return True, remaining
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # On error, allow the request
            return True, None
    
    def reset_rate_limit(self, user_id: str, limit_type: str):
        """Reset rate limit for a user (admin function)"""
        if not self.enabled:
            return
        
        key = self._make_key(user_id, limit_type)
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error resetting rate limit: {str(e)}")


# Global instance
rate_limiter = RateLimiter()


def check_rate_limit(user_id: str, tier: str, limit_type: str = 'api_calls_per_day') -> tuple[bool, Optional[int]]:
    """Convenience function to check rate limit"""
    return rate_limiter.check_rate_limit(user_id, tier, limit_type)

