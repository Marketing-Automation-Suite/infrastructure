"""
Mailgun Email Service Connector
"""

import httpx
from typing import Dict, Any, List
from .base_connector import BaseConnector


class MailgunConnector(BaseConnector):
    """Connector for Mailgun email API"""
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Mailgun API connection"""
        is_valid, error = self.validate_credentials(
            credentials,
            ["api_key", "domain"]
        )
        if not is_valid:
            return {
                "status": "failed",
                "message": error,
                "error": error
            }
        
        try:
            # Mailgun uses basic auth with api:api_key
            auth = ("api", credentials["api_key"])
            
            with httpx.Client() as client:
                response = client.get(
                    f"https://api.mailgun.net/v3/{credentials['domain']}",
                    auth=auth,
                    timeout=10.0
                )
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": "Mailgun connection successful",
                    "data": response.json()
                }
        except httpx.HTTPStatusError as e:
            return {
                "status": "failed",
                "message": f"Mailgun API error: {e.response.status_code}",
                "error": e.response.text
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection test failed: {str(e)}",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Get Mailgun capabilities"""
        return [
            "send_email",
            "send_bulk_email",
            "manage_contacts",
            "track_events",
            "validate_emails"
        ]
    
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Mailgun action"""
        return {
            "status": "not_implemented",
            "message": f"Action {action} not yet implemented",
            "action": action,
            "params": params
        }

