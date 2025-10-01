from typing import Annotated, AsyncGenerator
from fastapi import Depends
from app.application.use_cases import AgreementUseCases
from app.domain.repositories import AgreementRepository as AgreementRepoInterface
from app.infrastructure.repositories.agreement_repository import PostgresAgreementRepository
from app.infrastructure.postgres.session import AsyncSessionLocal

# Repositorio con manejo explícito de sesión
async def get_agreement_repository() -> AsyncGenerator[AgreementRepoInterface, None]:
    session = AsyncSessionLocal()
    try:
        repository =  PostgresAgreementRepository(session)
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
async def get_agreement_use_cases(
    repository: AgreementRepoInterface = Depends(get_agreement_repository)
) -> AgreementUseCases:
    return AgreementUseCases(repository)

# Aliases para usar en rutas
AgreementUseCasesDep = Annotated[AgreementUseCases, Depends(get_agreement_use_cases)]
AgreementRepositoryDep = Annotated[AgreementRepoInterface, Depends(get_agreement_repository)]