"""Store Pydantic schemas for validation."""

from datetime import datetime
from typing import Optional

from app.core.validators import validate_with_timing_protection
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


#region Base Schemas

class StoreBase(BaseModel):
    business_unit_id: int = Field(
        ..., 
        gt=0, 
        le=999999,
        description="Business unit identifier (1-999999)"
    )
    store_id: int = Field(
        ..., 
        gt=0, 
        le=999999,
        description="Store identifier (1-999999)"
    )
    name: str = Field(
        ..., 
        min_length=3,
        max_length=100,
        description="Store name (3-100 characters)"
    )
    zone_id: Optional[int] = Field(
        None, 
        gt=0, 
        le=999999,
        description="Zone identifier (1-999999)"
    )
    zone_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="Zone name (max 255 characters)"
    )
    channel_id: Optional[int] = Field(
        None, 
        gt=0, 
        le=999999,
        description="Channel identifier (1-999999)"
    )
    channel_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="Channel name (max 255 characters)"
    )

    @field_validator('name')
    @classmethod
    def validate_store_name(cls, v: str) -> str:
        return validate_with_timing_protection(
            value=v,
            field_name="store_name",
            min_length=3,
            max_length=100,
            allowed_chars=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)]+$',
            generic_names=['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
        )

    @field_validator('zone_name')
    @classmethod
    def validate_zone_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        sanitized = validate_with_timing_protection(
            value=v,
            field_name="zone_name",
            min_length=1,
            max_length=50,
            allowed_chars=r'^[A-Za-z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.]+$'
        )
        
        return sanitized if sanitized else None

    @field_validator('channel_name')
    @classmethod
    def validate_channel_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        sanitized = validate_with_timing_protection(
            value=v,
            field_name="channel_name",
            min_length=1,
            max_length=50,
            allowed_chars=r'^[A-Za-z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.]+$'
        )
        
        return sanitized if sanitized else None

#endregion


#region Response Schemas

class StoreResponse(StoreBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format."""
        return value.isoformat()

#endregion