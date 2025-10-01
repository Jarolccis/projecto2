"""Agreement Excluded Flag Pydantic schemas for validation and responses."""

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

class AgreementExcludedFlagBase(BaseModel):
    """Base schema for agreement excluded flag data."""
    
    flag_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Flag type (1-50 characters)"
    )
    flag_value: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Flag value (1-100 characters)"
    )

    @field_validator('flag_type')
    @classmethod
    def validate_flag_type(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Flag type",
            max_repeated_chars=3,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('flag_value')
    @classmethod
    def validate_flag_value(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Flag value",
            max_repeated_chars=3,
            normalize_whitespace=True,
            to_upper=False
        )

#endregion


#region Request Schemas

class AgreementExcludedFlagCreateRequest(BaseModel):
    """Schema for creating agreement excluded flags."""
    
    excluded_flag_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Excluded flag identifier (1-20 characters)"
    )

    @field_validator('excluded_flag_id')
    @classmethod
    def validate_excluded_flag_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Excluded flag ID",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

#endregion


#region Response Schemas

class AgreementExcludedFlagResponse(BaseModel):
    """Response schema for agreement excluded flags."""
    
    id: Optional[int] = None
    agreement_id: int
    excluded_flag_id: str
    active: bool
    created_at: Optional[str] = None
    created_by_user_email: str
    updated_status_by_user_email: Optional[str] = None
    updated_at: Optional[str] = None
    excluded_flag_name: Optional[str] = None

    model_config = {"from_attributes": True}


class AgreementExcludedFlagCreateResponse(BaseModel):
    """Response schema for created agreement excluded flags."""
    
    id: int
    agreement_id: int
    excluded_flag_id: str
    active: bool
    created_at: str
    created_by_user_email: str
    updated_at: str
    updated_status_by_user_email: Optional[str] = None

    model_config = {"from_attributes": True}

#endregion
