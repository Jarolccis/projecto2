"""Agreement Product Pydantic schemas for validation and responses."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from app.core.validators import validate_secure_string_advanced
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
)


#region Base Schemas

class AgreementProductBase(BaseModel):
    """Base schema for agreement product data."""
    
    sku_code: Optional[str] = Field(
        None,
        max_length=50,
        description="SKU code (max 50 characters)"
    )
    sku_description: Optional[str] = Field(
        None,
        max_length=255,
        description="SKU description (max 255 characters)"
    )
    division_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Division code (max 20 characters)"
    )
    division_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Division name (max 100 characters)"
    )
    department_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Department code (max 20 characters)"
    )
    department_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Department name (max 100 characters)"
    )
    subdepartment_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Subdepartment code (max 20 characters)"
    )
    subdepartment_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Subdepartment name (max 100 characters)"
    )
    class_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Class code (max 20 characters)"
    )
    class_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Class name (max 100 characters)"
    )
    subclass_code: Optional[str] = Field(
        None,
        max_length=20,
        description="Subclass code (max 20 characters)"
    )
    subclass_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Subclass name (max 100 characters)"
    )
    brand_id: Optional[str] = Field(
        None,
        max_length=20,
        description="Brand ID (max 20 characters)"
    )
    brand_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Brand name (max 100 characters)"
    )
    supplier_id: Optional[int] = Field(
        None,
        gt=0,
        le=999999999,
        description="Supplier ID (1-999999999)"
    )
    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name (max 255 characters)"
    )
    supplier_ruc: Optional[str] = Field(
        None,
        max_length=20,
        description="Supplier RUC"
    )

    @field_validator('sku_code')
    @classmethod
    def validate_sku_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.]+$',
            field_name="SKU code",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

#endregion


#region Request Schemas

class AgreementProductCreateRequest(AgreementProductBase):
    """Schema for creating agreement products."""
    pass

#endregion


#region Response Schemas

class AgreementProductResponse(BaseModel):
    """Response schema for agreement products."""
    
    id: Optional[int] = None
    agreement_id: int
    sku_code: Optional[str] = None
    sku_description: Optional[str] = None
    division_code: Optional[str] = None
    division_name: Optional[str] = None
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    subdepartment_code: Optional[str] = None
    subdepartment_name: Optional[str] = None
    class_code: Optional[str] = None
    class_name: Optional[str] = None
    subclass_code: Optional[str] = None
    subclass_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_ruc: Optional[str] = None
    active: bool
    created_at: Optional[str] = None
    created_by_user_email: str
    updated_status_by_user_email: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class AgreementProductCreateResponse(BaseModel):
    """Response schema for created agreement products."""
    
    id: int
    agreement_id: int
    sku_code: Optional[str] = None
    sku_description: Optional[str] = None
    division_code: Optional[str] = None
    division_name: Optional[str] = None
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    subdepartment_code: Optional[str] = None
    subdepartment_name: Optional[str] = None
    class_code: Optional[str] = None
    class_name: Optional[str] = None
    subclass_code: Optional[str] = None
    subclass_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_ruc: Optional[str] = None
    active: bool
    created_at: str
    created_by_user_email: str
    updated_status_by_user_email: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}

#endregion