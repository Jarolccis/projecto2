"""Agreements bulk upload repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.domain.entities.agreements_bulk_upload import (
    AgreementsBulkUploadDocument,
    AgreementsBulkUploadDocumentRow
)
from app.domain.entities.sku import Sku


class AgreementsBulkUploadRepository(ABC):
    """Abstract repository for agreements bulk upload operations."""

    @abstractmethod
    async def create_document(self, document: AgreementsBulkUploadDocument) -> AgreementsBulkUploadDocument:
        """Create a new bulk upload document."""
        pass

    @abstractmethod
    async def get_document_by_id(self, document_id: int) -> Optional[AgreementsBulkUploadDocument]:
        """Get document by ID."""
        pass

    @abstractmethod
    async def get_document_by_uid(self, document_uid: UUID) -> Optional[AgreementsBulkUploadDocument]:
        """Get document by UID."""
        pass

    @abstractmethod
    async def create_document_rows(self, rows: List[AgreementsBulkUploadDocumentRow]) -> List[AgreementsBulkUploadDocumentRow]:
        """Create multiple document rows."""
        pass

    @abstractmethod
    async def get_document_rows(self, document_id: int) -> List[AgreementsBulkUploadDocumentRow]:
        """Get all rows for a document."""
        pass

    @abstractmethod
    async def update_document_status(self, document_id: int, status_id: str, comments: Optional[str] = None) -> Optional[AgreementsBulkUploadDocument]:
        """Update document status and optionally comments."""
        pass

    @abstractmethod
    async def validate_document_rows(self, document_id: int, valid_skus: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Validate all rows in a bulk upload document using business rules.
        
        Args:
            document_id: The bulk document ID to validate
            valid_skus: Optional list of valid SKU codes to validate against
            
        Returns:
            Tuple[bool, str]: (success, message)
                - success: True if validation passed, False if issues found
                - message: Validation result message
        """
        pass

    @abstractmethod
    async def resolve_document_rows(self, document_id: int, resolved_by_user_email: str) -> Tuple[bool, str]:
        """
        Resolve all rows in a bulk upload document, converting text values to database IDs.
        
        Args:
            document_id: The bulk document ID to resolve
            resolved_by_user_email: Email of the user resolving the document
            
        Returns:
            Tuple[bool, str]: (success, message)
                - success: True if resolution completed successfully, False if issues found
                - message: Resolution result message
        """
        pass

    @abstractmethod
    async def create_agreements_from_resolved_rows(self, document_id: int, created_by_user_email: str, skus: List[Sku]) -> Tuple[bool, str, int]:
        """
        Create agreements and related tables from resolved document rows.
        This operation is transactional - all agreements are created or none.
        
        Args:
            document_id: The bulk document ID with resolved rows
            created_by_user_email: Email of the user creating the agreements
            skus: List of SKU entities with detailed information for enriching agreement products
            
        Returns:
            Tuple[bool, str, int]: (success, message, agreements_created_count)
                - success: True if all agreements were created successfully
                - message: Result message or error description
                - agreements_created_count: Number of agreements successfully created
        """
        pass

    @abstractmethod
    async def get_document_with_rows(self, document_id: int) -> Tuple[Optional[AgreementsBulkUploadDocument], List[AgreementsBulkUploadDocumentRow]]:
        """
        Get document and its rows in a single database operation to optimize connection usage.
        
        Args:
            document_id: The document ID to retrieve
            
        Returns:
            Tuple containing:
                - document: The document entity or None if not found
                - rows: List of document rows (empty if document not found)
        """
        pass
