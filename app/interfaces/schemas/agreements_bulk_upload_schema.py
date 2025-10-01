"""Agreements bulk upload schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.agreement_enums import SourceSystemEnum


#region Base Schemas

class AgreementsBulkUploadDocumentBase(BaseModel):
    """Base schema for bulk upload document with common fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    business_unit_id: int = Field(..., description="Business unit ID")
    status_id: str = Field(..., max_length=10, description="Document status ID")
    full_path_document: Optional[str] = Field(None, description="Full path to the document")
    comments: Optional[str] = Field(None, description="Document comments")
    document_uid: UUID = Field(..., description="Unique document identifier")
    source_system: Optional[SourceSystemEnum] = Field(None, description="Source system type")
    created_by_user_email: str = Field(..., max_length=320, description="User email who created the document")


class AgreementsBulkUploadDocumentSchema(AgreementsBulkUploadDocumentBase):
    """Schema for bulk upload document with all fields."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BulkUploadRowSchema(BaseModel):
    """Schema for individual bulk upload row data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    pmm_user: Optional[str] = Field(None, max_length=150, description="PMM User")
    group_name: Optional[str] = Field(None, max_length=150, description="Grouping")
    excluded_flags: Optional[str] = Field(None, max_length=150, description="Excluded flags")
    included_stores: Optional[str] = Field(None, description="Included stores")
    excluded_stores: Optional[str] = Field(None, description="Excluded stores")
    rebate_type: Optional[str] = Field(None, max_length=100, description="Rebate type")
    concept: Optional[str] = Field(None, max_length=100, description="Concept")
    note: Optional[str] = Field(None, max_length=150, description="Description")
    spf_code: Optional[str] = Field(None, max_length=50, description="SPF code")
    spf_description: Optional[str] = Field(None, max_length=255, description="SPF description")
    sku: Optional[str] = Field(None, max_length=50, description="SKU")
    start_date: Optional[str] = Field(None, max_length=50, description="Start date")
    end_date: Optional[str] = Field(None, max_length=50, description="End date")
    unit_rebate_pen: Optional[str] = Field(None, max_length=50, description="Unit rebate in PEN")
    billing_type: Optional[str] = Field(None, max_length=150, description="Billing type")
    observations: Optional[str] = Field(None, description="Observations")

#endregion


#region Request Schemas

class BulkUploadRequest(BaseModel):
    """Schema for bulk upload request validation."""
    
    source_system_type: SourceSystemEnum = Field(..., description="Source system type (SPF or PMM)")

#endregion


#region Response Schemas

class BulkUploadProcessResponse(BaseModel):
    """Schema for bulk upload process response."""
    
    document_id: Optional[int] = None
    document_uid: Optional[UUID] = None
    total_rows_processed: int
    valid_rows: int
    invalid_rows: int
    processing_status: str
    file_name: str
    processing_time_seconds: float
    validation_errors: List[str] = []
    final_status: str


class BulkUploadDocumentResponse(BaseModel):
    """Schema for bulk upload document response."""
    
    document: AgreementsBulkUploadDocumentSchema
    total_rows: int


class BulkUploadDocumentResolutionResponse(BaseModel):
    """Schema for bulk upload document resolution response with agreements creation info."""
    
    document: AgreementsBulkUploadDocumentSchema
    total_rows: int
    resolution_success: bool
    resolution_message: str
    agreements_created: int = 0
    agreements_creation_success: bool = False
    processing_time_seconds: float


class TemplateDownloadResponse(BaseModel):
    """Schema for template download response."""
    
    source_system_type: SourceSystemEnum
    template_name: str
    download_url: str
    expires_in_minutes: int = 10

#endregion
