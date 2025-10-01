from typing import Annotated, AsyncGenerator
from fastapi import Depends
from app.application.use_cases.lookup_use_cases import LookupUseCases
from app.domain.repositories.lookup_repository import LookupRepository as LookupRepoInterface
from app.infrastructure.repositories.lookup_repository import PostgresLookupRepository
from app.infrastructure.postgres.session import AsyncSessionLocal

# Repositorio con manejo explícito de sesión
async def get_lookup_repository() -> AsyncGenerator[LookupRepoInterface, None]:
    session = AsyncSessionLocal()
    try:
        repository = PostgresLookupRepository(session)
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
async def get_lookup_use_cases(
    repository: LookupRepoInterface = Depends(get_lookup_repository)
) -> LookupUseCases:
    return LookupUseCases(repository)

# Aliases para usar en rutas
LookupUseCasesDep = Annotated[LookupUseCases, Depends(get_lookup_use_cases)]
LookupRepositoryDep = Annotated[LookupRepoInterface, Depends(get_lookup_repository)]
