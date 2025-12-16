"""
Clearbit Data Enrichment Connector
"""

import httpx
from typing import Dict, Any, List
from .base_connector import BaseConnector


class ClearbitConnector(BaseConnector):
    """Connector for Clearbit data enrichment API"""
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Clearbit API connection"""
        is_valid, error = self.validate_credentials(credentials, ["api_key"])
        if not is_valid:
            return {
                "status": "failed",
                "message": error,
                "error": error
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {credentials['api_key']}"
            }
            
            # Test with a simple person lookup
            with httpx.Client() as client:
                # Use discovery API as a simple test
                response = client.get(
                    "https://person.clearbit.com/v2/combined/find",
                    headers=headers,
                    params={"email": "test@example.com"},
                    timeout=10.0
                )
                # 404 is acceptable for test email, 401/403 means auth failed
                if response.status_code in [401, 403]:
                    return {
                        "status": "failed",
                        "message": "Clearbit API authentication failed",
                        "error": response.text
                    }
                
                return {
                    "status": "success",
                    "message": "Clearbit connection successful",
                    "data": {"api_key_valid": True}
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                return {
                    "status": "failed",
                    "message": "Clearbit API authentication failed",
                    "error": e.response.text
                }
            return {
                "status": "failed",
                "message": f"Clearbit API error: {e.response.status_code}",
                "error": e.response.text
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection test failed: {str(e)}",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Get Clearbit capabilities"""
        return [
            "enrich_person",
            "enrich_company",
            "enrich_domain",
            "find_company",
            "discover_company"
        ]
    
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Clearbit action"""
        return {
            "status": "not_implemented",
            "message": f"Action {action} not yet implemented",
            "action": action,
            "params": params
        }

