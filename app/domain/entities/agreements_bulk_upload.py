"""Agreements bulk upload domain entities."""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from app.core.agreement_enums import SourceSystemEnum


@dataclass
class AgreementsBulkUploadDocument:
    """Domain entity for agreements bulk upload document."""
    
    id: Optional[int]
    business_unit_id: int
    status_id: str
    full_path_document: Optional[str]
    comments: Optional[str]
    document_uid: UUID
    source_system: Optional[SourceSystemEnum]
    created_at: datetime
    created_by_user_email: str
    updated_at: datetime

    @classmethod
    def create(
        cls,
        business_unit_id: int,
        status_id: str,
        created_by_user_email: str,
        source_system: Optional[SourceSystemEnum] = None,
        full_path_document: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> "AgreementsBulkUploadDocument":
        """Create a new bulk upload document instance."""
        now = datetime.utcnow()
        return cls(
            id=None,
            business_unit_id=business_unit_id,
            status_id=status_id,
            full_path_document=full_path_document,
            comments=comments,
            document_uid=uuid4(),
            source_system=source_system,
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_at=now,
        )

    def update_status(self, status_id: str) -> None:
        """Update document status."""
        self.status_id = status_id
        self.updated_at = datetime.utcnow()

    def update_path(self, full_path_document: str) -> None:
        """Update document path."""
        self.full_path_document = full_path_document
        self.updated_at = datetime.utcnow()


@dataclass
class AgreementsBulkUploadDocumentRow:
    """Domain entity for agreements bulk upload document row."""
    
    id: Optional[int]
    bulk_document_id: int
    pmm_user: Optional[str]
    group_name: Optional[str]
    excluded_flags: Optional[str]
    included_stores: Optional[str]
    excluded_stores: Optional[str]
    rebate_type: Optional[str]
    concept: Optional[str]
    note: Optional[str]
    spf_code: Optional[str]
    spf_description: Optional[str]
    sku: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    unit_rebate_pen: Optional[str]
    billing_type: Optional[str]
    observations: Optional[str]
    active: bool
    created_at: datetime
    created_by_user_email: str
    updated_at: datetime
    
    # Resolved fields
    pmm_user_id: Optional[str] = None
    group_id: Optional[str] = None
    rebate_type_id: Optional[str] = None
    concept_id: Optional[str] = None
    billing_type_id: Optional[str] = None
    included_store_ids: Optional[List[int]] = None
    excluded_store_ids: Optional[List[int]] = None
    excluded_flag_ids: Optional[List[str]] = None
    start_date_parsed: Optional[date] = None
    end_date_parsed: Optional[date] = None
    unit_rebate_num: Optional[Decimal] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    @classmethod
    def create(
        cls,
        bulk_document_id: int,
        created_by_user_email: str,
        **kwargs
    ) -> "AgreementsBulkUploadDocumentRow":
        """Create a new bulk upload document row instance."""
        now = datetime.utcnow()
        return cls(
            id=None,
            bulk_document_id=bulk_document_id,
            pmm_user=kwargs.get('pmm_user'),
            group_name=kwargs.get('group_name'),
            excluded_flags=kwargs.get('excluded_flags'),
            included_stores=kwargs.get('included_stores'),
            excluded_stores=kwargs.get('excluded_stores'),
            rebate_type=kwargs.get('rebate_type'),
            concept=kwargs.get('concept'),
            note=kwargs.get('note'),
            spf_code=kwargs.get('spf_code'),
            spf_description=kwargs.get('spf_description'),
            sku=kwargs.get('sku'),
            start_date=kwargs.get('start_date'),
            end_date=kwargs.get('end_date'),
            unit_rebate_pen=kwargs.get('unit_rebate_pen'),
            billing_type=kwargs.get('billing_type'),
            observations=kwargs.get('observations'),
            active=kwargs.get('active', True),
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_at=now,
            
            # New resolved fields (initially None when creating)
            pmm_user_id=kwargs.get('pmm_user_id'),
            group_id=kwargs.get('group_id'),
            rebate_type_id=kwargs.get('rebate_type_id'),
            concept_id=kwargs.get('concept_id'),
            billing_type_id=kwargs.get('billing_type_id'),
            included_store_ids=kwargs.get('included_store_ids'),
            excluded_store_ids=kwargs.get('excluded_store_ids'),
            excluded_flag_ids=kwargs.get('excluded_flag_ids'),
            start_date_parsed=kwargs.get('start_date_parsed'),
            end_date_parsed=kwargs.get('end_date_parsed'),
            unit_rebate_num=kwargs.get('unit_rebate_num'),
            resolved_at=kwargs.get('resolved_at'),
            resolved_by=kwargs.get('resolved_by'),
        )

    def deactivate(self) -> None:
        """Deactivate the row."""
        self.active = False
        self.updated_at = datetime.utcnow()
