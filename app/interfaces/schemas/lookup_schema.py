"""Lookup Pydantic schemas for validation."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.core.validators import validate_with_timing_protection
from app.core.response import BaseResponse, SuccessResponse
from app.domain.entities.lookup import LookupValueResult


#region Request Schemas

class LookupCategoryCodeRequest(BaseModel):
    """Schema for validating category code input."""
    
    category_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Category code (2-50 characters)"
    )
    
    @field_validator('category_code')
    @classmethod
    def validate_category_code(cls, v: str) -> str:
        """Validate category code with enhanced security validation."""
        return validate_with_timing_protection(
            value=v,
            field_name="Category code",
            min_length=2,
            max_length=50,
            allowed_chars=r'^[A-Z0-9_]+$',
            generic_names=['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
        )


class LookupOptionValueRequest(BaseModel):
    """Schema for validating option value input."""
    
    category_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Category code (2-50 characters)"
    )
    option_value: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Option value (1-100 characters)"
    )
    
    @field_validator('category_code')
    @classmethod
    def validate_category_code(cls, v: str) -> str:
        """Validate category code with enhanced security validation."""
        return validate_with_timing_protection(
            value=v,
            field_name="Category code",
            min_length=2,
            max_length=50,
            allowed_chars=r'^[A-Z0-9_]+$',
            generic_names=['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
        )
    
    @field_validator('option_value')
    @classmethod
    def validate_option_value(cls, v: str) -> str:
        """Validate option value with enhanced security validation."""
        return validate_with_timing_protection(
            value=v,
            field_name="Option value",
            min_length=1,
            max_length=100,
            allowed_chars=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)\_\%\@]+$',
            generic_names=['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
        )

#endregion


#region Response Schemas

class LookupValueResponse(BaseModel):
    """Response schema for individual lookup value data."""
    
    lookup_value_id: int
    option_key: str
    display_value: str
    option_value: str
    metadata: dict = {}
    sort_order: Optional[int] = None
    parent_id: Optional[int] = None
    
    @classmethod
    def from_domain_model(cls, domain_model: LookupValueResult) -> 'LookupValueResponse':
        """Create LookupValueResponse from domain model."""
        return cls(
            lookup_value_id=domain_model.lookup_value_id,
            option_key=domain_model.option_key,
            display_value=domain_model.display_value,
            option_value=domain_model.option_value,
            metadata=domain_model.metadata,
            sort_order=domain_model.sort_order,
            parent_id=domain_model.parent_id
        )


class LookupValueSingleResponse(SuccessResponse[LookupValueResponse]):
    """Response schema for single lookup value with success wrapper."""
    
    @classmethod
    def from_domain_model(cls, domain_model: LookupValueResult, category_code: str, option_value: str) -> 'LookupValueSingleResponse':
        """Create LookupValueSingleResponse from domain model."""
        lookup_value = LookupValueResponse.from_domain_model(domain_model)
        return cls(
            data=lookup_value,
            message=f"Retrieved lookup value for category {category_code} and option {option_value}"
        )


class LookupValuesResponse(SuccessResponse[List[LookupValueResponse]]):
    """Response schema for multiple lookup values with success wrapper."""
    
    count: int
    
    @classmethod
    def from_domain_models(cls, domain_models: List[LookupValueResult], category_code: str) -> 'LookupValuesResponse':
        """Create LookupValuesResponse from domain models."""
        values = [LookupValueResponse.from_domain_model(model) for model in domain_models]
        return cls(
            data=values,
            message=f"Retrieved {len(values)} lookup values for category {category_code}",
            count=len(values)
        )

#endregion


#region Legacy Schemas (for backward compatibility)

class LookupCategoryCodeSchema(LookupCategoryCodeRequest):
    """Legacy schema for backward compatibility."""
    pass


class LookupOptionValueSchema(LookupOptionValueRequest):
    """Legacy schema for backward compatibility."""
    pass

#endregion
