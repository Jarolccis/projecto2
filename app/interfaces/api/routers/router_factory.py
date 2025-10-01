"""Router factory for dynamic router creation based on configuration."""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

from app.core.logging import LoggerMixin
from .router_config import ROUTER_CONFIGS, get_enabled_routers, refresh_router_configs
from .router_discovery import get_router_discovery, get_enabled_routers as get_discovered_enabled_routers


class RouterFactory(LoggerMixin):
    def __init__(self):
        self.discovery = get_router_discovery()
        self._validate_configuration()
        self._main_router: Optional[APIRouter] = None
    
    def _validate_configuration(self) -> None:
        try:
            validation = self.validate_router_configuration()
            if not validation["valid"]:
                missing = validation["missing_implementations"]
                extra = validation["extra_implementations"]
                
                if missing:
                    self.log_warning(
                        "Routers configurados pero no implementados", 
                        missing_implementations=missing
                    )
                if extra:
                    self.log_warning(
                        "Routers implementados pero no configurados", 
                        extra_implementations=extra
                    )
            else:
                self.log_info("Configuración de routers validada correctamente")
                
        except Exception as e:
            self.log_error(
                "Error al validar configuración de routers", 
                error=e
            )
            raise
    
    def create_main_router(self) -> APIRouter:
        if self._main_router is not None:
            return self._main_router
        
        self._main_router = APIRouter()
        enabled_routers = get_discovered_enabled_routers()
        
        self.log_info(
            "Creando router principal", 
            total_routers_enabled=len(enabled_routers)
        )
        
        # Incluir solo los routers habilitados y descubiertos
        for router_name, metadata in enabled_routers.items():
            try:
                # Los routers ya tienen su propio prefijo definido, no duplicar
                self._main_router.include_router(
                    metadata.router_instance
                ) 
                self.log_info(
                    "Router incluido exitosamente", 
                    router_name=router_name,
                    prefix=metadata.prefix,
                    tags=metadata.tags
                )
            except Exception as e:
                self.log_error(
                    "Error al incluir router",
                    router_name=router_name,
                    error=e
                )
        
        self.log_info("Router principal creado exitosamente")
        return self._main_router
    
    def get_router_by_name(self, router_name: str) -> Optional[APIRouter]:
        metadata = self.discovery.get_router_by_name(router_name)
        return metadata.router_instance if metadata else None
    
    def get_all_implemented_routers(self) -> List[str]:
        return list(self.discovery.get_discovered_routers().keys())
    
    def get_missing_implementations(self) -> List[str]:
        configured = set(ROUTER_CONFIGS.keys())
        implemented = set(self.discovery.get_discovered_routers().keys())
        return list(configured - implemented)
    
    def validate_router_configuration(self) -> Dict[str, Any]:
        configured = set(ROUTER_CONFIGS.keys())
        implemented = set(self.discovery.get_discovered_routers().keys())
        
        missing = list(configured - implemented)
        extra = list(implemented - configured)
        
        return {
            "valid": len(missing) == 0 and len(extra) == 0,
            "missing_implementations": missing,
            "extra_implementations": extra,
            "total_configured": len(configured),
            "total_implemented": len(implemented)
        }
    
    def clear_cache(self) -> None:
        self._main_router = None
        self.log_debug("Caché del router principal limpiado")


# Instancia singleton del factory
_router_factory = RouterFactory()


@lru_cache(maxsize=1)
def create_api_router() -> APIRouter: 
    return _router_factory.create_main_router()


def get_router_status() -> Dict[str, Any]:
    discovery_status = _router_factory.discovery.get_discovery_status()
    
    return {
        "configuration": {name: {
            "name": config.name,
            "prefix": config.prefix,
            "tags": config.tags,
            "description": config.description,
            "enabled": config.enabled,
            "version": config.version
        } for name, config in ROUTER_CONFIGS.items()},
        "implementations": _router_factory.get_all_implemented_routers(),
        "validation": _router_factory.validate_router_configuration(),
        "enabled": get_enabled_routers(),
        "discovery": discovery_status,
        "cache_status": {
            "main_router_cached": _router_factory._main_router is not None
        }
    }


def clear_router_cache() -> None:
    """Clear the router cache to force recreation."""
    _router_factory.clear_cache()
    create_api_router.cache_clear()
    _router_factory.log_info("Caché de routers limpiado")


def reload_routers() -> APIRouter:
    """Reload all routers from discovery."""
    # Refresh discovery
    _router_factory.discovery.refresh_discovery()
    
    # Refresh configurations
    refresh_router_configs()
    
    # Clear caches
    clear_router_cache()
    
    # Create new router
    return create_api_router()
