"""Dynamic router discovery system.""" 
import importlib 
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from app.core.logging import LoggerMixin

class RouterMetadata:
    """Metadata for router discovery."""
    
    def __init__(
        self,
        name: str,
        module_path: str,
        router_instance: APIRouter,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        version: str = "v1"
    ):
        self.name = name
        self.module_path = module_path
        self.router_instance = router_instance
        self.prefix = prefix or f"/{name}"
        self.tags = tags or [name]
        self.description = description or f"API para {name}"
        self.enabled = enabled
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "module_path": self.module_path,
            "prefix": self.prefix,
            "tags": self.tags,
            "description": self.description,
            "enabled": self.enabled,
            "version": self.version
        }


class RouterDiscovery(LoggerMixin):
    """Dynamic router discovery system."""
    
    def __init__(self, controllers_path: str = "app.interfaces.api.controllers"):
        self.controllers_path = controllers_path
        self._discovered_routers: Dict[str, RouterMetadata] = {}
        self._scan_controllers()
    
    def _scan_controllers(self) -> None:
        """Scan controllers directory for routers."""
        try:
            self.log_info("Iniciando descubrimiento dinámico de routers")
            
            # Get the controllers directory path
            controllers_dir = Path(__file__).parent.parent / "controllers"
            
            if not controllers_dir.exists():
                self.log_warning("Directorio de controllers no encontrado", path=str(controllers_dir))
                return
            
            # Scan all Python files in controllers directory
            for file_path in controllers_dir.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                
                self._process_controller_file(file_path)
            
            self.log_info(
                "Descubrimiento de routers completado",
                total_routers=len(self._discovered_routers),
                router_names=list(self._discovered_routers.keys())
            )
            
        except Exception as e:
            self.log_error("Error durante el descubrimiento de routers", error=e)
            raise
    
    def _process_controller_file(self, file_path: Path) -> None:
        """Process a single controller file."""
        try:
            module_name = file_path.stem
            full_module_path = f"{self.controllers_path}.{module_name}"
            
            self.log_debug("Procesando archivo de controller", file=module_name)
            
            # Import the module
            module = importlib.import_module(full_module_path)
            
            # Look for router instance
            router_instance = self._find_router_in_module(module, module_name)
            
            if router_instance:
                # Extract metadata from router
                metadata = self._extract_router_metadata(module, module_name, router_instance)
                self._discovered_routers[module_name] = metadata
                
                self.log_info(
                    "Router descubierto exitosamente",
                    router_name=module_name,
                    prefix=metadata.prefix,
                    tags=metadata.tags
                )
            else:
                self.log_debug("No se encontró router en el módulo", module=module_name)
                
        except Exception as e:
            self.log_warning(
                "Error al procesar archivo de controller",
                file=str(file_path),
                error=e
            )
    
    def _find_router_in_module(self, module: Any, module_name: str) -> Optional[APIRouter]:
        """Find router instance in module."""
        # Look for common router variable names
        router_names = ["router", f"{module_name}_router", "api_router"]
        
        for router_name in router_names:
            if hasattr(module, router_name):
                router = getattr(module, router_name)
                if isinstance(router, APIRouter):
                    return router
        
        # Look for any APIRouter instance in module attributes
        for attr_name in dir(module):
            if not attr_name.startswith("_"):
                attr = getattr(module, attr_name)
                if isinstance(attr, APIRouter):
                    return attr
        
        return None
    
    def _extract_router_metadata(
        self, 
        module: Any, 
        module_name: str, 
        router: APIRouter
    ) -> RouterMetadata:
        """Extract metadata from router instance."""
        # Default values
        prefix = f"/{module_name}"
        tags = [module_name]
        description = f"API para {module_name}"
        enabled = True
        version = "v1"
        
        # Try to extract from router attributes
        if hasattr(router, 'prefix') and router.prefix:
            prefix = router.prefix
        
        if hasattr(router, 'tags') and router.tags:
            tags = router.tags
        
        # Try to extract from module docstring or comments
        if hasattr(module, '__doc__') and module.__doc__:
            description = module.__doc__.strip()
        
        # Look for configuration in module
        if hasattr(module, 'ROUTER_CONFIG'):
            config = getattr(module, 'ROUTER_CONFIG')
            if isinstance(config, dict):
                prefix = config.get('prefix', prefix)
                tags = config.get('tags', tags)
                description = config.get('description', description)
                enabled = config.get('enabled', enabled)
                version = config.get('version', version)
        
        return RouterMetadata(
            name=module_name,  # Keep original name as key
            module_path=f"{self.controllers_path}.{module_name}",
            router_instance=router,
            prefix=prefix,  # Use clean prefix
            tags=tags,
            description=description,
            enabled=enabled,
            version=version
        )
    
    def get_discovered_routers(self) -> Dict[str, RouterMetadata]:
        """Get all discovered routers."""
        return self._discovered_routers.copy()
    
    def get_router_by_name(self, name: str) -> Optional[RouterMetadata]:
        """Get router metadata by name."""
        return self._discovered_routers.get(name)
    
    def get_enabled_routers(self) -> Dict[str, RouterMetadata]:
        """Get only enabled routers."""
        return {
            name: metadata 
            for name, metadata in self._discovered_routers.items() 
            if metadata.enabled
        }
    
    def refresh_discovery(self) -> None:
        """Refresh router discovery."""
        self._discovered_routers.clear()
        self._scan_controllers()
        self.log_info("Descubrimiento de routers actualizado")
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Get discovery status information."""
        enabled_routers = self.get_enabled_routers()
        
        return {
            "total_discovered": len(self._discovered_routers),
            "total_enabled": len(enabled_routers),
            "routers": {
                name: metadata.to_dict() 
                for name, metadata in self._discovered_routers.items()
            },
            "enabled_routers": list(enabled_routers.keys())
        }


# Global discovery instance
_router_discovery = RouterDiscovery()


def get_router_discovery() -> RouterDiscovery:
    """Get the global router discovery instance."""
    return _router_discovery


def refresh_router_discovery() -> None:
    """Refresh the global router discovery."""
    _router_discovery.refresh_discovery()


def get_discovered_routers() -> Dict[str, RouterMetadata]:
    """Get all discovered routers."""
    return _router_discovery.get_discovered_routers()


def get_enabled_routers() -> Dict[str, RouterMetadata]:
    """Get only enabled routers."""
    return _router_discovery.get_enabled_routers()
