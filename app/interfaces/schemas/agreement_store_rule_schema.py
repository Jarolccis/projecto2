"""Agreement Store Rule Pydantic schemas for validation and responses."""

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

class AgreementStoreRuleBase(BaseModel):
    """Base schema for agreement store rule data."""
    
    store_id: int = Field(
        ...,
        gt=0,
        le=999999999,
        description="Store ID (1-999999999)"
    )
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Store rule status (1-50 characters)"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Store rule status",
            max_repeated_chars=3,
            normalize_whitespace=True,
            to_upper=False
        )

#endregion


#region Request Schemas

class AgreementStoreRuleCreateRequest(AgreementStoreRuleBase):
    """Schema for creating agreement store rules."""
    pass

#endregion


#region Response Schemas

class AgreementStoreRuleResponse(BaseModel):
    """Response schema for agreement store rules."""
    
    id: Optional[int] = None
    agreement_id: int
    store_id: int
    status: str
    active: bool
    created_at: Optional[str] = None
    created_by_user_email: str
    updated_status_by_user_email: Optional[str] = None
    updated_at: Optional[str] = None
    store_name: Optional[str] = None  # Store name from store catalog

    model_config = {"from_attributes": True}


class AgreementStoreRuleCreateResponse(BaseModel):
    """Response schema for created agreement store rules."""
    
    id: int
    agreement_id: int
    store_id: int
    status: str
    active: bool
    created_at: str
    created_by_user_email: str
    updated_status_by_user_email: Optional[str] = None
    updated_at: str

    model_config = {"from_attributes": True}
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True
    }

#endregion
