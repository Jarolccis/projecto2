"""Module dependencies for FastAPI dependency injection."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.application.use_cases.modules_use_cases import ModulesUseCases
from app.domain.repositories.modules_repository import ModulesRepository as ModulesRepoInterface
from app.infrastructure.repositories.modules_repository import ModulesRepository as ConcreteModulesRepository
from app.infrastructure.postgres.session import AsyncSessionLocal

# Repositorio con manejo explícito de sesión
async def get_module_repository() -> AsyncGenerator[ModulesRepoInterface, None]:
    session = AsyncSessionLocal()
    try:
        repository = ConcreteModulesRepository(session)
        yield repository
        # Auto-commit on successful completion
        await session.commit()
    except Exception:
        # Auto-rollback on any exception
        await session.rollback()
        raise
    finally:
        # Ensure session is closed
        await session.close()

# Use case que recibe el repositorio como dependencia
async def get_module_use_cases(
    repository: ModulesRepoInterface = Depends(get_module_repository)
) -> ModulesUseCases:
    return ModulesUseCases(module_repository=repository)

# Type aliases for cleaner dependency injection
ModuleRepositoryDep = Annotated[ModulesRepoInterface, Depends(get_module_repository)]
ModuleUseCasesDep = Annotated[ModulesUseCases, Depends(get_module_use_cases)]
