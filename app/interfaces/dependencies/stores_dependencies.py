from typing import Annotated, AsyncGenerator
from fastapi import Depends
from app.application.use_cases import StoresUseCases
from app.domain.repositories import StoresRepository as StoresRepoInterface
from app.infrastructure.repositories import StoresRepository as PostgresStoresRepo
from app.infrastructure.postgres.session import AsyncSessionLocal

# Repositorio con manejo explícito de sesión
async def get_store_repository() -> AsyncGenerator[StoresRepoInterface, None]:
    session = AsyncSessionLocal()
    try:
        repository = PostgresStoresRepo(session)
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
async def get_store_use_cases(
    store_repository: StoresRepoInterface = Depends(get_store_repository),
) -> StoresUseCases:
    return StoresUseCases(store_repository)

StoreUseCasesDep = Annotated[StoresUseCases, Depends(get_store_use_cases)]
StoreRepositoryDep = Annotated[StoresRepoInterface, Depends(get_store_repository)]
