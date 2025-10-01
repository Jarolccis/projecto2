"""Master data dependencies for dependency injection.

This module contains all dependencies related to master data operations:
- Master data repository factory
- Master data use cases factory
- Type aliases for cleaner route signatures
"""

from typing import Annotated

from fastapi import Depends

from app.application.use_cases.master_data_use_cases import MasterDataUseCases
from app.domain.repositories.master_data_repository import MasterDataRepository
from app.infrastructure.repositories.master_data_repository import (
    MasterDataRepository,
)


def get_master_data_repository() -> MasterDataRepository:
    """Factory function for MasterDataRepository.

    Uses BigQuery repository for master data. Application will fail if BigQuery is unavailable.
    """
    try:
        # BigQuery connection validation could be added here
        return MasterDataRepository()
    except Exception as e:
        # En caso de error, lanzar excepción para que la aplicación falle
        raise Exception(f"Failed to initialize BigQuery master data repository: {e}")


def get_master_data_use_cases(
    master_data_repository: Annotated[MasterDataRepository, Depends(get_master_data_repository)],
) -> MasterDataUseCases:
    """Factory function for MasterDataUseCases.

    This demonstrates dependency injection - MasterDataUseCases depends on MasterDataRepository,
    and FastAPI automatically injects the repository when creating use cases.
    """
    return MasterDataUseCases(master_data_repository)


# Type aliases for cleaner route signatures
MasterDataUseCasesDep = Annotated[MasterDataUseCases, Depends(get_master_data_use_cases)]
MasterDataRepositoryDep = Annotated[MasterDataRepository, Depends(get_master_data_repository)]
