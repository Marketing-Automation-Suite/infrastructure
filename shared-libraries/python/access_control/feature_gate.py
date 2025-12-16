"""
Feature gate utilities
"""

from typing import List
from .tier_checker import tier_checker, TIER_LIMITS


class FeatureGate:
    """Control feature access by tier"""
    
    def check_feature_access(self, tier: str, feature: str) -> bool:
        """
        Check if user tier has access to a feature
        
        Args:
            tier: User tier
            feature: Feature name
            
        Returns:
            True if user has access, False otherwise
        """
        limits = tier_checker.get_tier_limits(tier)
        features = limits.get('features', [])
        return feature in features
    
    def get_available_features(self, tier: str) -> List[str]:
        """Get list of available features for a tier"""
        limits = tier_checker.get_tier_limits(tier)
        return limits.get('features', [])
    
    def require_feature(self, tier: str, feature: str) -> bool:
        """
        Require a feature (raises exception if not available)
        
        Args:
            tier: User tier
            feature: Required feature
            
        Returns:
            True if available
            
        Raises:
            PermissionError if feature not available
        """
        if not self.check_feature_access(tier, feature):
            raise PermissionError(f"Feature '{feature}' requires a higher tier. Current tier: {tier}")
        return True


# Global instance
feature_gate = FeatureGate()


def check_feature_access(tier: str, feature: str) -> bool:
    """Convenience function to check feature access"""
    return feature_gate.check_feature_access(tier, feature)

