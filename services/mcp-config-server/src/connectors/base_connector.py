"""
Abstract base class for service connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Abstract base class for all service connectors.
    
    All service connectors must implement:
    - test_connection(): Test if credentials work
    - get_capabilities(): List what the service can do
    - execute_action(): Perform service-specific actions
    """
    
    def __init__(self, service_id: str, service_name: str):
        """
        Initialize connector.
        
        Args:
            service_id: Unique service identifier
            service_name: Human-readable service name
        """
        self.service_id = service_id
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_id}")
    
    @abstractmethod
    def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connection to the external service.
        
        Args:
            credentials: Service credentials dictionary
            
        Returns:
            Dictionary with:
                - status: "success" or "failed"
                - message: Human-readable message
                - data: Optional response data
                - error: Optional error message if failed
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this service provides.
        
        Returns:
            List of capability strings (e.g., ["generate_leads", "enrich_profiles"])
        """
        pass
    
    @abstractmethod
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a service-specific action.
        
        Args:
            action: Action name (e.g., "generate_leads", "send_email")
            params: Action parameters
            credentials: Service credentials
            
        Returns:
            Dictionary with action result
        """
        pass
    
    def validate_credentials(self, credentials: Dict[str, Any], required_fields: List[str]) -> tuple[bool, Optional[str]]:
        """
        Validate that required credential fields are present.
        
        Args:
            credentials: Credentials dictionary
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        missing = [field for field in required_fields if field not in credentials or not credentials[field]]
        if missing:
            return False, f"Missing required credentials: {', '.join(missing)}"
        return True, None
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get basic service information.
        
        Returns:
            Dictionary with service metadata
        """
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "capabilities": self.get_capabilities()
        }

