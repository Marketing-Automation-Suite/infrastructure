"""
Tier checking utilities
"""

import httpx
from typing import Optional, Dict
import os
import logging

logger = logging.getLogger(__name__)

# Tier hierarchy
TIER_ORDER = {'free': 0, 'bronze': 1, 'silver': 2, 'gold': 3}

# Tier limits configuration
TIER_LIMITS = {
    'free': {
        'max_contacts': 100,
        'max_workflows': 5,
        'api_calls_per_day': 100,
        'features': ['basic_dashboard', 'basic_analytics']
    },
    'bronze': {
        'max_contacts': 1000,
        'max_workflows': 20,
        'api_calls_per_day': 1000,
        'features': ['advanced_analytics', 'api_access']
    },
    'silver': {
        'max_contacts': 10000,
        'max_workflows': -1,  # unlimited
        'api_calls_per_day': 10000,
        'features': ['unlimited_workflows', 'api_access', 'webhooks']
    },
    'gold': {
        'max_contacts': -1,  # unlimited
        'max_workflows': -1,
        'api_calls_per_day': -1,  # unlimited
        'features': ['all_features', 'white_label', 'custom_integrations']
    }
}


class TierChecker:
    """Check user tier and access permissions"""
    
    def __init__(self):
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8001')
        self.token_verification_url = os.getenv('TOKEN_VERIFICATION_URL', 'http://token-verification-service:8002')
    
    async def get_user_tier(self, user_id: str, wallet_address: Optional[str] = None) -> str:
        """
        Get user's tier from auth service or token verification
        
        Args:
            user_id: User ID from auth service
            wallet_address: Optional wallet address for token verification
            
        Returns:
            Tier string (free, bronze, silver, gold)
        """
        # First, try to get tier from auth service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_service_url}/v1/users/{user_id}/tier",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('tier', 'free')
        except Exception as e:
            logger.warning(f"Error getting tier from auth service: {str(e)}")
        
        # If wallet address provided, check token verification
        if wallet_address:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.token_verification_url}/v1/user-tiers/{wallet_address}",
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        tiers = data.get('tiers', [])
                        if tiers:
                            # Get highest tier
                            highest_tier = 'free'
                            for tier_info in tiers:
                                tier = tier_info.get('tier', 'free')
                                if TIER_ORDER.get(tier, 0) > TIER_ORDER.get(highest_tier, 0):
                                    highest_tier = tier
                            return highest_tier
            except Exception as e:
                logger.warning(f"Error getting tier from token verification: {str(e)}")
        
        return 'free'
    
    def check_tier_access(self, user_tier: str, required_tier: str) -> bool:
        """
        Check if user tier meets required tier
        
        Args:
            user_tier: User's current tier
            required_tier: Required tier for access
            
        Returns:
            True if user has access, False otherwise
        """
        user_level = TIER_ORDER.get(user_tier, 0)
        required_level = TIER_ORDER.get(required_tier, 0)
        return user_level >= required_level
    
    def get_tier_limits(self, tier: str) -> Dict:
        """Get limits for a tier"""
        return TIER_LIMITS.get(tier, TIER_LIMITS['free'])
    
    def check_limit(self, tier: str, limit_type: str, current_value: int) -> bool:
        """
        Check if current value is within tier limit
        
        Args:
            tier: User tier
            limit_type: Type of limit (max_contacts, max_workflows, etc.)
            current_value: Current value
            
        Returns:
            True if within limit, False if exceeded
        """
        limits = self.get_tier_limits(tier)
        limit = limits.get(limit_type, 0)
        
        # -1 means unlimited
        if limit == -1:
            return True
        
        return current_value < limit


# Global instance
tier_checker = TierChecker()


async def get_user_tier(user_id: str, wallet_address: Optional[str] = None) -> str:
    """Convenience function to get user tier"""
    return await tier_checker.get_user_tier(user_id, wallet_address)


def check_tier_access(user_tier: str, required_tier: str) -> bool:
    """Convenience function to check tier access"""
    return tier_checker.check_tier_access(user_tier, required_tier)

