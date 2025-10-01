"""FastAPI dependencies for dependency injection.

This module provides a centralized way to manage all application dependencies
by organizing them into logical modules and providing clean imports.
"""

from .lookup_dependencies import (
    LookupRepositoryDep,
    LookupUseCasesDep,
    get_lookup_repository,
    get_lookup_use_cases,
)
from .master_data_dependencies import (
    MasterDataRepositoryDep,
    MasterDataUseCasesDep,
    get_master_data_repository,
    get_master_data_use_cases,
)

from .modules_dependencies import (
    ModuleRepositoryDep,
    ModuleUseCasesDep,
    get_module_repository,
    get_module_use_cases,
)

from .stores_dependencies import (
    StoreRepositoryDep,
    StoreUseCasesDep,
    get_store_repository,
    get_store_use_cases,
)
from .agreement_dependencies import (
    AgreementUseCasesDep,
    get_agreement_repository,
    get_agreement_use_cases,
)
from .sku_dependencies import (
    SkuRepositoryDep,
    SkuUseCasesDep,
    get_sku_repository,
    get_sku_use_cases,
)

__all__ = [
    # Store dependencies
    "get_store_repository",
    "get_store_use_cases", 
    "StoreUseCasesDep",
    "StoreRepositoryDep", 
    
    # Lookup dependencies
    "get_lookup_repository",
    "get_lookup_use_cases",
    "LookupUseCasesDep",
    "LookupRepositoryDep",
    
    # Master data dependencies
    "get_master_data_repository",
    "get_master_data_use_cases",
    "MasterDataUseCasesDep",
    "MasterDataRepositoryDep",

    # Module dependencies
    "get_module_repository",
    "get_module_use_cases",
    "ModuleUseCasesDep",
    "ModuleRepositoryDep",
    
    # Agreement dependencies
    "get_agreement_repository",
    "get_agreement_use_cases",
    "AgreementUseCasesDep",
    
    # SKU dependencies
    "get_sku_repository",
    "get_sku_use_cases",
    "SkuUseCasesDep",
    "SkuRepositoryDep",
]
