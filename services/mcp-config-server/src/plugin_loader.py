"""
Dynamic plugin loader for service connectors
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Type, Optional, Any, List
from .connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Dynamically discovers and loads connector classes from the connectors directory.
    """
    
    def __init__(self, connectors_path: Optional[Path] = None):
        """
        Initialize plugin loader.
        
        Args:
            connectors_path: Path to connectors directory.
                           Defaults to src/connectors/
        """
        if connectors_path:
            self.connectors_path = connectors_path
        else:
            # Default to connectors directory relative to this file
            current_dir = Path(__file__).parent
            self.connectors_path = current_dir / "connectors"
        
        self._connector_classes: Dict[str, Type[BaseConnector]] = {}
        self._loaded_connectors: Dict[str, BaseConnector] = {}
        self._discover_connectors()
    
    def _discover_connectors(self):
        """Discover all connector classes in the connectors directory."""
        if not self.connectors_path.exists():
            logger.warning(f"Connectors path does not exist: {self.connectors_path}")
            return
        
        # Get all Python files in connectors directory (excluding __init__.py and base_connector.py)
        connector_files = [
            f for f in self.connectors_path.glob("*.py")
            if f.name not in ["__init__.py", "base_connector.py"]
        ]
        
        for connector_file in connector_files:
            try:
                self._load_connector_from_file(connector_file)
            except Exception as e:
                logger.error(f"Error loading connector from {connector_file}: {str(e)}")
    
    def _load_connector_from_file(self, connector_file: Path):
        """
        Load connector class from a Python file.
        
        Args:
            connector_file: Path to connector Python file
        """
        # Get module name (e.g., "connectors.linkedin_connector")
        module_name = f"src.connectors.{connector_file.stem}"
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find all classes that inherit from BaseConnector
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseConnector) and 
                    obj != BaseConnector and 
                    obj.__module__ == module_name):
                    
                    # Get service_id from class (should be set as class attribute or in __init__)
                    # For now, derive from class name (e.g., LinkedInConnector -> linkedin)
                    service_id = self._derive_service_id(name)
                    
                    self._connector_classes[service_id] = obj
                    logger.info(f"Loaded connector class: {name} (service_id: {service_id})")
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing connector file {connector_file}: {str(e)}")
    
    def _derive_service_id(self, class_name: str) -> str:
        """
        Derive service_id from connector class name.
        
        Args:
            class_name: Connector class name (e.g., "LinkedInConnector")
            
        Returns:
            Service ID (e.g., "linkedin")
        """
        # Remove "Connector" suffix if present
        if class_name.endswith("Connector"):
            class_name = class_name[:-9]
        
        # Convert PascalCase to snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        service_id = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        return service_id
    
    def get_connector_class(self, service_id: str) -> Optional[Type[BaseConnector]]:
        """
        Get connector class for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Connector class or None if not found
        """
        return self._connector_classes.get(service_id)
    
    def create_connector(self, service_id: str, service_name: str) -> Optional[BaseConnector]:
        """
        Create a connector instance for a service.
        
        Args:
            service_id: Service identifier
            service_name: Human-readable service name
            
        Returns:
            Connector instance or None if not found
        """
        connector_class = self.get_connector_class(service_id)
        if connector_class:
            try:
                connector = connector_class(service_id, service_name)
                self._loaded_connectors[service_id] = connector
                return connector
            except Exception as e:
                logger.error(f"Error creating connector for {service_id}: {str(e)}")
                return None
        return None
    
    def get_connector(self, service_id: str) -> Optional[BaseConnector]:
        """
        Get existing connector instance or create a new one.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Connector instance or None
        """
        # Check if already loaded
        if service_id in self._loaded_connectors:
            return self._loaded_connectors[service_id]
        
        # Try to create new instance
        # We need service_name from registry
        from .registry.service_registry import get_registry
        registry = get_registry()
        service_def = registry.get_service(service_id)
        service_name = service_def.get("name", service_id) if service_def else service_id
        
        return self.create_connector(service_id, service_name)
    
    def list_available_connectors(self) -> List[str]:
        """
        List all available connector service IDs.
        
        Returns:
            List of service IDs
        """
        return list(self._connector_classes.keys())
    
    def reload(self):
        """Reload all connectors from disk."""
        self._connector_classes.clear()
        self._loaded_connectors.clear()
        self._discover_connectors()
        logger.info("Plugin loader reloaded")


# Global plugin loader instance
_plugin_loader: Optional[PluginLoader] = None


def get_plugin_loader() -> PluginLoader:
    """
    Get or create global plugin loader instance.
    
    Returns:
        PluginLoader instance
    """
    global _plugin_loader
    if _plugin_loader is None:
        _plugin_loader = PluginLoader()
    return _plugin_loader

