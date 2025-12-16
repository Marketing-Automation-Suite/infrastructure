"""
Service registry and discovery system
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Manages service definitions and discovery.
    Loads service definitions from YAML files and provides discovery capabilities.
    """
    
    def __init__(self, definitions_path: Optional[str] = None):
        """
        Initialize service registry.
        
        Args:
            definitions_path: Path to service definitions directory.
                            Defaults to src/registry/service_definitions/
        """
        if definitions_path:
            self.definitions_path = Path(definitions_path)
        else:
            # Default to service_definitions directory relative to this file
            current_dir = Path(__file__).parent
            self.definitions_path = current_dir / "service_definitions"
        
        self._services: Dict[str, Dict[str, Any]] = {}
        self._load_all_definitions()
    
    def _load_all_definitions(self):
        """Load all service definitions from YAML files."""
        if not self.definitions_path.exists():
            logger.warning(f"Service definitions path does not exist: {self.definitions_path}")
            return
        
        for yaml_file in self.definitions_path.glob("*.yaml"):
            try:
                service_def = self._load_definition(yaml_file)
                if service_def:
                    service_id = service_def.get("id")
                    if service_id:
                        self._services[service_id] = service_def
                        logger.info(f"Loaded service definition: {service_id}")
            except Exception as e:
                logger.error(f"Error loading service definition from {yaml_file}: {str(e)}")
    
    def _load_definition(self, yaml_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single service definition from YAML file.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            Service definition dictionary or None if invalid
        """
        try:
            with open(yaml_file, 'r') as f:
                definition = yaml.safe_load(f)
            
            # Validate required fields
            if not definition.get("id"):
                logger.error(f"Service definition missing 'id' field: {yaml_file}")
                return None
            
            if not definition.get("name"):
                logger.error(f"Service definition missing 'name' field: {yaml_file}")
                return None
            
            # Set definition path
            definition["definition_path"] = str(yaml_file)
            
            return definition
        except Exception as e:
            logger.error(f"Error parsing YAML file {yaml_file}: {str(e)}")
            return None
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get service definition by ID.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Service definition dictionary or None
        """
        return self._services.get(service_id)
    
    def list_services(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all services with optional filtering.
        
        Args:
            category: Filter by category (e.g., "lead_generation", "email")
            search_query: Search in name and description
            active_only: Only return active services
            
        Returns:
            List of service definitions
        """
        services = list(self._services.values())
        
        # Filter by category
        if category:
            services = [s for s in services if s.get("category") == category]
        
        # Filter by search query
        if search_query:
            query_lower = search_query.lower()
            services = [
                s for s in services
                if query_lower in s.get("name", "").lower()
                or query_lower in s.get("description", "").lower()
            ]
        
        # Filter active services
        if active_only:
            services = [s for s in services if s.get("is_active", True)]
        
        return services
    
    def search_marketplace(
        self,
        use_case: Optional[str] = None,
        integration_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search marketplace for services.
        
        Args:
            use_case: Search by use case (e.g., "lead generation", "email marketing")
            integration_type: Search by integration type
            category: Filter by category
            
        Returns:
            List of matching service definitions
        """
        services = self.list_services(category=category, active_only=True)
        
        # Filter by use case
        if use_case:
            use_case_lower = use_case.lower()
            services = [
                s for s in services
                if use_case_lower in s.get("description", "").lower()
                or use_case_lower in s.get("name", "").lower()
                or any(use_case_lower in cap.lower() for cap in s.get("capabilities", []))
            ]
        
        # Filter by integration type
        if integration_type:
            services = [
                s for s in services
                if integration_type.lower() in s.get("category", "").lower()
            ]
        
        return services
    
    def get_service_capabilities(self, service_id: str) -> List[str]:
        """
        Get capabilities for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of capability strings
        """
        service = self.get_service(service_id)
        if service:
            return service.get("capabilities", [])
        return []
    
    def get_configuration_steps(self, service_id: str) -> List[Dict[str, Any]]:
        """
        Get configuration steps for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of configuration step dictionaries
        """
        service = self.get_service(service_id)
        if service:
            return service.get("configuration_steps", [])
        return []
    
    def get_required_credentials(self, service_id: str) -> List[str]:
        """
        Get required credentials for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of required credential field names
        """
        service = self.get_service(service_id)
        if service:
            return service.get("required_credentials", [])
        return []
    
    def get_optional_credentials(self, service_id: str) -> List[str]:
        """
        Get optional credentials for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of optional credential field names
        """
        service = self.get_service(service_id)
        if service:
            return service.get("optional_credentials", [])
        return []
    
    def reload(self):
        """Reload all service definitions from disk."""
        self._services.clear()
        self._load_all_definitions()
        logger.info("Service registry reloaded")


# Global registry instance
_registry: Optional[ServiceRegistry] = None


def get_registry() -> ServiceRegistry:
    """
    Get or create global service registry instance.
    
    Returns:
        ServiceRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry

