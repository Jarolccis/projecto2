"""Agreements bulk upload dependencies for FastAPI dependency injection."""

from typing import Annotated, AsyncGenerator
from fastapi import Depends
from contextlib import asynccontextmanager
from app.infrastructure.postgres.session import _db_manager
from app.application.use_cases.agreements_bulk_upload_use_cases import AgreementsBulkUploadUseCases
from app.domain.repositories.agreements_bulk_upload_repository import AgreementsBulkUploadRepository
from app.infrastructure.repositories.agreements_bulk_upload_repository import (
    AgreementsBulkUploadRepository as AgreementsBulkUploadRepositoryImpl,
)
from app.core.utils import ExcelProcessing
from app.interfaces.dependencies.sku_dependencies import SkuRepositoryDep

async def get_bulk_upload_repository() -> AsyncGenerator[AgreementsBulkUploadRepository, None]:
    """Get agreements bulk upload repository with transactional session."""  
    async with _db_manager.AsyncSessionLocal() as session:
        try:
            repository = AgreementsBulkUploadRepositoryImpl(session)
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
        # Session auto-closes due to async context manager


def get_excel_processing_service() -> ExcelProcessing:
    """
    Get Excel processing utility instance.
    
    Returns:
        ExcelProcessing: Utility for processing Excel files
    """
    return ExcelProcessing()


def get_bulk_upload_use_cases(
    bulk_upload_repository: Annotated[AgreementsBulkUploadRepository, Depends(get_bulk_upload_repository)],
    excel_service: Annotated[ExcelProcessing, Depends(get_excel_processing_service)],
    sku_repository: SkuRepositoryDep
) -> AgreementsBulkUploadUseCases:
    """
    Get agreements bulk upload use cases instance.
    
    Args:
        bulk_upload_repository: Bulk upload repository dependency
        excel_service: Excel processing utility dependency
        sku_repository: SKU repository dependency
        
    Returns:
        AgreementsBulkUploadUseCases: Bulk upload use cases instance
    """
    return AgreementsBulkUploadUseCases(
        bulk_upload_repository=bulk_upload_repository,
        excel_service=excel_service,
        sku_repository=sku_repository
    )


# Type aliases for cleaner dependency injection
BulkUploadRepositoryDep = Annotated[AgreementsBulkUploadRepository, Depends(get_bulk_upload_repository)]
ExcelProcessingServiceDep = Annotated[ExcelProcessing, Depends(get_excel_processing_service)]
BulkUploadUseCasesDep = Annotated[AgreementsBulkUploadUseCases, Depends(get_bulk_upload_use_cases)]
