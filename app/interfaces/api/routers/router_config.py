from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional
from app.core.logging import LoggerMixin
from .router_discovery import get_router_discovery, RouterMetadata

@dataclass
class RouterConfig:
    name: str
    prefix: str
    tags: List[str]
    description: str
    enabled: bool = True
    version: str = "v1"
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del router no puede estar vacío")
        
        if not self.prefix or not self.prefix.strip():
            raise ValueError("El prefijo del router no puede estar vacío")
        
        if not self.prefix.startswith('/'):
            raise ValueError("El prefijo debe comenzar con '/'")
        
        if not self.tags or len(self.tags) == 0:
            raise ValueError("El router debe tener al menos un tag")
        
        if not self.description or not self.description.strip():
            raise ValueError("El router debe tener una descripción")
    
    @classmethod
    def from_metadata(cls, metadata: RouterMetadata) -> 'RouterConfig':
        """Create RouterConfig from RouterMetadata."""
        return cls(
            name=metadata.name,
            prefix=metadata.prefix,
            tags=metadata.tags,
            description=metadata.description,
            enabled=metadata.enabled,
            version=metadata.version
        )


def _get_dynamic_router_configs() -> Dict[str, RouterConfig]:
    """Get router configurations dynamically from discovery."""
    discovery = get_router_discovery()
    discovered_routers = discovery.get_discovered_routers()
    
    configs = {}
    for name, metadata in discovered_routers.items():
        try:
            configs[name] = RouterConfig.from_metadata(metadata)
        except Exception as e:
            # Log error but continue with other routers
            temp_logger = LoggerMixin()
            temp_logger.log_warning(
                "Error al crear configuración de router",
                router_name=name,
                error=e
            )
    
    return configs


# Dynamic router configurations - no longer hardcoded!
ROUTER_CONFIGS: Dict[str, RouterConfig] = _get_dynamic_router_configs()

# Validar todas las configuraciones al cargar el módulo
def _validate_all_configs() -> None:
    try:
        # Crear un logger temporal para la validación del módulo
        temp_logger = LoggerMixin()
        
        for name, config in ROUTER_CONFIGS.items():
            temp_logger.log_debug("Validando configuración del router", router_name=name)
            # La validación se ejecuta automáticamente en __post_init__
        
        temp_logger.log_info(
            "Todas las configuraciones de routers validadas", 
            total_routers=len(ROUTER_CONFIGS)
        )
        
    except Exception as e:
        # En caso de error, usar logging apropiado
        temp_logger.log_error(f"Error al validar configuraciones de routers: {e}")
        raise

# Ejecutar validación al cargar el módulo
_validate_all_configs()


def refresh_router_configs() -> None:
    """Refresh router configurations from discovery."""
    global ROUTER_CONFIGS
    ROUTER_CONFIGS = _get_dynamic_router_configs()
    _validate_all_configs()
    
    # Clear caches
    get_enabled_routers.cache_clear()
    get_all_router_configs.cache_clear()


@lru_cache(maxsize=1)
def get_enabled_routers() -> List[str]:
    enabled = [name for name, config in ROUTER_CONFIGS.items() if config.enabled]
    return enabled


def get_router_config(router_name: str) -> RouterConfig:
    if router_name not in ROUTER_CONFIGS:
        raise KeyError(f"Router '{router_name}' no encontrado")
    
    return ROUTER_CONFIGS[router_name]


@lru_cache(maxsize=1)
def get_all_router_configs() -> Dict[str, RouterConfig]:
    return ROUTER_CONFIGS.copy()


def add_router_config(
    name: str,
    prefix: str,
    tags: List[str],
    description: str,
    enabled: bool = True,
    version: str = "v1"
) -> None:
    """Agrega una nueva configuración de router.
    
    Args:
        name: Nombre único del router
        prefix: Prefijo de la ruta
        tags: Lista de tags para la documentación
        description: Descripción del router
        enabled: Si el router está habilitado
        version: Versión del router
        
    Raises:
        ValueError: Si ya existe un router con ese nombre
    """
    if name in ROUTER_CONFIGS:
        raise ValueError(f"Router '{name}' ya existe")
    
    new_config = RouterConfig(
        name=name,
        prefix=prefix,
        tags=tags,
        description=description,
        enabled=enabled,
        version=version
    )
    
    ROUTER_CONFIGS[name] = new_config
    get_enabled_routers.cache_clear()
    get_all_router_configs.cache_clear()



def remove_router_config(name: str) -> None:
    """Elimina una configuración de router.
    
    Args:
        name: Nombre del router a eliminar
        
    Raises:
        KeyError: Si el router no existe
    """
    if name not in ROUTER_CONFIGS:
        raise KeyError(f"Router '{name}' no encontrado")
    
    del ROUTER_CONFIGS[name] 


def update_router_config(
    name: str,
    **kwargs
) -> None:
    """Actualiza una configuración de router existente.
    
    Args:
        name: Nombre del router a actualizar
        **kwargs: Campos a actualizar
        
    Raises:
        KeyError: Si el router no existe
        ValueError: Si se intenta actualizar campos no permitidos
    """
    if name not in ROUTER_CONFIGS:
        raise KeyError(f"Router '{name}' no encontrado")
    
    config = ROUTER_CONFIGS[name]
    
    # Solo permitir actualizar ciertos campos
    allowed_fields = {'enabled', 'description', 'tags', 'version'}
    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(config, field, value)
        else:
            raise ValueError(f"No se puede actualizar el campo '{field}'")


def get_router_by_prefix(prefix: str) -> Optional[str]:
    """Obtiene el nombre del router por su prefijo.
    
    Args:
        prefix: Prefijo a buscar
        
    Returns:
        Nombre del router o None si no se encuentra
    """
    for name, config in ROUTER_CONFIGS.items():
        if config.prefix == prefix:
            return name
    return None
