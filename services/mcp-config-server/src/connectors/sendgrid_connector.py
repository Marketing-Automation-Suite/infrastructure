"""
SendGrid Email Service Connector
"""

import httpx
from typing import Dict, Any, List
from .base_connector import BaseConnector


class SendGridConnector(BaseConnector):
    """Connector for SendGrid email API"""
    
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test SendGrid API connection"""
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
            
            with httpx.Client() as client:
                response = client.get(
                    "https://api.sendgrid.com/v3/user/profile",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": "SendGrid connection successful",
                    "data": response.json()
                }
        except httpx.HTTPStatusError as e:
            return {
                "status": "failed",
                "message": f"SendGrid API error: {e.response.status_code}",
                "error": e.response.text
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection test failed: {str(e)}",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Get SendGrid capabilities"""
        return [
            "send_email",
            "send_bulk_email",
            "manage_contacts",
            "create_campaigns",
            "track_opens",
            "track_clicks"
        ]
    
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SendGrid action"""
        return {
            "status": "not_implemented",
            "message": f"Action {action} not yet implemented",
            "action": action,
            "params": params
        }

