"""Agreement Pydantic schemas for validation and responses."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from app.core.validators import validate_with_timing_protection, validate_secure_string_advanced
from app.core.agreement_enums import SourceSystemEnum
from app.core.response import SuccessResponse
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

# Import schemas from separated files
from .agreement_product_schema import (
    AgreementProductCreateRequest,
    AgreementProductResponse,
    AgreementProductCreateResponse
)
from .agreement_store_rule_schema import (
    AgreementStoreRuleCreateRequest,
    AgreementStoreRuleResponse,
    AgreementStoreRuleCreateResponse
)
from .agreement_excluded_flag_schema import (
    AgreementExcludedFlagCreateRequest,
    AgreementExcludedFlagResponse,
    AgreementExcludedFlagCreateResponse
)


#region Base Schemas

class AgreementBase(BaseModel):
    """Base schema for agreement data."""
    
    agreement_number: int = Field(
        ...,
        ge=1,
        le=999999999,
        description="Agreement number (1-999999999)"
    )
    description: str = Field(
        ..., 
        min_length=1, 
        max_length=70,
        description="Agreement description (1-70 characters)"
    )
    rebate_type_id: str = Field(
        ...,
        max_length=50,
        description="Rebate type identifier"
    )
    source_system: SourceSystemEnum = Field(
        ...,
        description="Source system for the agreement"
    )
    start_date: date = Field(
        ...,
        description="Agreement start date"
    )
    end_date: date = Field(
        ...,
        description="Agreement end date"
    )
    business_unit_id: Optional[int] = Field(
        ...,
        gt=0,
        le=999999999,
        description="Business unit ID (1-999999999)"
    )
    agreement_type_id: Optional[str] = Field(
        None, 
        max_length=50,
        description="Agreement type identifier"
    )
    activity_name: Optional[str] = Field(
        None, 
        max_length=100,
        description="Activity name"
    )
    currency_id: Optional[int] = Field(
        None, 
        gt=0,
        le=999999999,
        description="Currency ID"
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Unit price (0.00-999999.99)"
    )
    billing_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Billing type"
    )
    pmm_username: Optional[str] = Field(
        None, 
        max_length=100,
        description="PMM username"
    )
    store_grouping_id: Optional[str] = Field(
        None, 
        max_length=50,
        description="Store grouping identifier"
    )
    spf_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="SPF code"
    )
    spf_description: Optional[str] = Field(
        None, 
        max_length=255,
        description="SPF description"
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="Agreement description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('rebate_type_id')
    @classmethod
    def validate_rebate_type_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Rebate type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('agreement_type_id')
    @classmethod
    def validate_agreement_type_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Agreement type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('activity_name')
    @classmethod
    def validate_activity_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="Activity name",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('billing_type')
    @classmethod
    def validate_billing_type(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Billing type",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.@]+$',
            field_name="PMM username",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('store_grouping_id')
    @classmethod
    def validate_store_grouping_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Store grouping ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Allows any character
            field_name="SPF code",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Allows any character
            field_name="SPF description",
            normalize_whitespace=True,
            to_upper=False
        )

    @model_validator(mode='after')
    def validate_dates(self) -> 'AgreementBase':
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self

    @model_validator(mode='after')
    def validate_spf_code_for_pmm(self) -> 'AgreementBase':
        if self.source_system == SourceSystemEnum.PMM and (self.spf_code is None or self.spf_code.strip() == ""):
            self.spf_code = None
        return self


#region Request Schemas

class AgreementSearchRequest(BaseModel):
    """Schema for searching agreements."""
    
    division_codes: Optional[List[str]] = Field(
        None,
        description="List of division codes to filter by"
    )
    status_ids: Optional[List[str]] = Field(
        None,
        description="List of status IDs to filter by"
    )
    created_by_emails: Optional[List[str]] = Field(
        None,
        description="List of creator emails to filter by"
    )
    agreement_number: Optional[int] = Field(
        None, 
        ge=1,
        le=999999999,
        description="Agreement number to search for"
    )
    sku_code: Optional[str] = Field(
        None,
        max_length=50,
        description="SKU code to search for"
    )
    description: Optional[str] = Field(
        None, 
        max_length=70,
        description="Agreement description to search for"
    )
    rebate_type_id: Optional[str] = Field(
        None, 
        max_length=50,
        description="Rebate type ID to filter by"
    )
    concept_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Concept ID to filter by"
    )
    spf_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="SPF code to search for"
    )
    spf_description: Optional[str] = Field(
        None, 
        max_length=255,
        description="SPF description to search for"
    )
    start_date: Optional[date] = Field(
        None, 
        description="Start date to filter by"
    )
    end_date: Optional[date] = Field(
        None,
        description="End date to filter by"
    )
    supplier_ruc: Optional[str] = Field(
        None,
        max_length=20,
        description="Supplier RUC to search for"
    )
    supplier_name: Optional[str] = Field(
        None, 
        max_length=255,
        description="Supplier name to search for"
    )
    store_grouping_id: Optional[str] = Field(
        None, 
        max_length=50,
        description="Store grouping ID to filter by"
    )
    pmm_username: Optional[str] = Field(
        None,
        max_length=100,
        description="PMM username to filter by"
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of results to skip"
    )

    @field_validator('division_codes')
    @classmethod
    def validate_division_codes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return [validate_secure_string_advanced(
            value=code,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Division code",
            normalize_whitespace=False,
            to_upper=False
        ) for code in v]

    @field_validator('status_ids')
    @classmethod
    def validate_status_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return [validate_secure_string_advanced(
            value=status_id,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Status ID",
            normalize_whitespace=False,
            to_upper=False
        ) for status_id in v]

    @field_validator('created_by_emails')
    @classmethod
    def validate_created_by_emails(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        return [validate_secure_string_advanced(
            value=email,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.@]+$',
            field_name="Creator email",
            normalize_whitespace=False,
            to_upper=False
        ) for email in v]

    @field_validator('sku_code')
    @classmethod
    def validate_sku_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.]+$',
            field_name="SKU code",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="Agreement description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('rebate_type_id')
    @classmethod
    def validate_rebate_type_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Rebate type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('concept_id')
    @classmethod
    def validate_concept_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Concept ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="SPF code",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="SPF description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('supplier_ruc')
    @classmethod
    def validate_supplier_ruc(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Supplier RUC",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('supplier_name')
    @classmethod
    def validate_supplier_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="Supplier name",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('store_grouping_id')
    @classmethod
    def validate_store_grouping_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Store grouping ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.@]+$',
            field_name="PMM username",
            normalize_whitespace=False,
            to_upper=False
        )

    @model_validator(mode='after')
    def validate_dates(self) -> 'AgreementSearchRequest':
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self


class AgreementCreateRequest(BaseModel):
    """Schema for creating agreements."""
    
    start_date: Optional[date] = Field(None, description="Agreement start date")
    end_date: Optional[date] = Field(None, description="Agreement end date")
    rebate_type_id: str = Field(..., max_length=50, description="Rebate type identifier")
    concept_id: str = Field(..., max_length=50, description="Concept identifier")
    activity_name: Optional[str] = Field(None, max_length=100, description="Activity name")
    source_system: SourceSystemEnum = Field(..., description="Source system for the agreement")
    spf_code: Optional[str] = Field(None, max_length=50, description="SPF code")
    spf_description: Optional[str] = Field(None, max_length=255, description="SPF description")
    store_grouping_id: Optional[str] = Field(None, max_length=50, description="Store grouping identifier")
    excluded_flags: List[AgreementExcludedFlagCreateRequest] = Field(
        default_factory=list,
        description="List of excluded flags"
    )
    unit_price: Decimal = Field(..., ge=0, decimal_places=2, description="Unit price")
    billing_type: str = Field(..., min_length=1, max_length=50, description="Billing type")
    pmm_username: Optional[str] = Field(None, max_length=100, description="PMM username")
    description: str = Field(..., min_length=1, max_length=70, description="Agreement description")
    products: List[AgreementProductCreateRequest] = Field(
        ...,
            min_length=1,
        description="List of products (minimum 1 required)"
    )
    currency_id: Optional[int] = Field(None, gt=0, le=999999999, description="Currency ID")
    status_id: str = Field(..., max_length=50, description="Status identifier")
    store_rules: List[AgreementStoreRuleCreateRequest] = Field(
        default_factory=list,
        description="List of store rules"
    )
    business_unit_id: Optional[int] = Field(..., gt=0, le=999999999, description="Business unit ID")
    agreement_number: Optional[int] = Field(None, ge=1, le=999999999, description="Agreement number")
    agreement_type_id: Optional[str] = Field(None, max_length=50, description="Agreement type identifier")

    @field_validator('rebate_type_id')
    @classmethod
    def validate_rebate_type_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Rebate type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('concept_id')
    @classmethod
    def validate_concept_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Concept ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('activity_name')
    @classmethod
    def validate_activity_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Allows any character
            field_name="Activity name",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Allows any character
            field_name="SPF code",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Allows any character
            field_name="SPF description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('store_grouping_id')
    @classmethod
    def validate_store_grouping_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Store grouping ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('billing_type')
    @classmethod
    def validate_billing_type(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Billing type",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.@]+$',
            field_name="PMM username",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',
            field_name="Agreement description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('status_id')
    @classmethod
    def validate_status_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Status ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('agreement_type_id')
    @classmethod
    def validate_agreement_type_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Agreement type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @model_validator(mode='after')
    def validate_dates(self) -> 'AgreementCreateRequest':
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self

    @model_validator(mode='after')
    def validate_products(self) -> 'AgreementCreateRequest':
        if not self.products:
            raise ValueError("At least one product is required")
        return self

    @model_validator(mode='after')
    def validate_spf_code_for_pmm(self) -> 'AgreementCreateRequest':
        if self.source_system == SourceSystemEnum.PMM and (self.spf_code is None or self.spf_code.strip() == ""):
            self.spf_code = None
        return self


class AgreementUpdateRequest(BaseModel):
    """Schema for updating agreements."""
    
    start_date: Optional[date] = Field(None, description="Agreement start date")
    end_date: Optional[date] = Field(None, description="Agreement end date")
    rebate_type_id: str = Field(..., max_length=50, description="Rebate type identifier")
    concept_id: str = Field(..., max_length=50, description="Concept identifier")
    activity_name: Optional[str] = Field(None, max_length=100, description="Activity name")
    source_system: SourceSystemEnum = Field(..., description="Source system for the agreement")
    spf_code: Optional[str] = Field(None, max_length=50, description="SPF code")
    spf_description: Optional[str] = Field(None, max_length=255, description="SPF description")
    store_grouping_id: Optional[str] = Field(None, max_length=50, description="Store grouping identifier")
    excluded_flags: List[AgreementExcludedFlagCreateRequest] = Field(
        default_factory=list,
        description="List of excluded flags"
    )
    unit_price: Decimal = Field(..., ge=0, decimal_places=2, description="Unit price")
    billing_type: str = Field(..., min_length=1, max_length=50, description="Billing type")
    pmm_username: Optional[str] = Field(None, max_length=100, description="PMM username")
    description: str = Field(..., min_length=1, max_length=70, description="Agreement description")
    products: List[AgreementProductCreateRequest] = Field(
        ...,
        min_length=1,
        description="List of products (minimum 1 required)"
    )
    currency_id: Optional[int] = Field(None, gt=0, le=999999999, description="Currency ID")
    status_id: str = Field(..., max_length=50, description="Status identifier")
    store_rules: List[AgreementStoreRuleCreateRequest] = Field(
        default_factory=list,
        description="List of store rules"
    )
    business_unit_id: Optional[int] = Field(None, gt=0, le=999999999, description="Business unit ID")
    agreement_type_id: Optional[str] = Field(None, max_length=50, description="Agreement type identifier")

    @field_validator('rebate_type_id')
    @classmethod
    def validate_rebate_type_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Rebate type ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('concept_id')
    @classmethod
    def validate_concept_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Concept ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('activity_name')
    @classmethod
    def validate_activity_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Permite cualquier carácter
            field_name="Activity name",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Permite cualquier carácter
            field_name="SPF code",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Permite cualquier carácter
            field_name="SPF description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('store_grouping_id')
    @classmethod
    def validate_store_grouping_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Store grouping ID",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('billing_type')
    @classmethod
    def validate_billing_type(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\s]+$',
            field_name="Billing type",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.@]+$',
            field_name="PMM username",
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'.*',  # Permite cualquier carácter
            field_name="Agreement description",
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('status_id')
    @classmethod
    def validate_status_id(cls, v: str) -> str:
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Status ID",
            normalize_whitespace=False,
            to_upper=False
        )

    # @field_validator('agreement_type_id')
    # @classmethod
    # def validate_agreement_type_id(cls, v: Optional[str]) -> Optional[str]:
    #     if v is None:
    #         return v
    #     return validate_secure_string_advanced(
    #         value=v,
    #         allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
    #         field_name="Agreement type ID",
    #         normalize_whitespace=False,
    #         to_upper=False
    #     )

    @model_validator(mode='after')
    def validate_dates(self) -> 'AgreementUpdateRequest':
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self

    @model_validator(mode='after')
    def validate_products(self) -> 'AgreementUpdateRequest':
        if not self.products:
            raise ValueError("At least one product is required")
        return self

    @model_validator(mode='after')
    def validate_spf_code_for_pmm(self) -> 'AgreementUpdateRequest':
        if self.source_system == SourceSystemEnum.PMM and (self.spf_code is None or self.spf_code.strip() == ""):
            self.spf_code = None
        return self


#endregion


#region Response Schemas

class AgreementResponse(BaseModel):
    """Response schema for agreements."""
    
    id: int
    business_unit_id: int
    agreement_number: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    agreement_type_id: Optional[str] = None
    status_id: str
    status_name: Optional[str] = None
    rebate_type_id: str
    concept_id: str
    description: Optional[str] = None
    activity_name: Optional[str] = None
    source_system: SourceSystemEnum
    spf_code: Optional[str] = None
    spf_description: Optional[str] = None
    currency_id: Optional[int] = None
    unit_price: Decimal
    billing_type: str
    pmm_username: Optional[str] = None
    store_grouping_id: Optional[str] = None
    bulk_upload_document_id: Optional[int] = None
    active: bool
    created_at: str
    created_by_user_email: Optional[str]
    updated_at: str
    updated_status_by_user_email: Optional[str] = None
    
    # Lookup descriptions
    status_description: Optional[str] = None
    rebate_type_description: Optional[str] = None
    concept_description: Optional[str] = None
    billing_type_description: Optional[str] = None
    pmm_username_description: Optional[str] = None
    store_grouping_description: Optional[str] = None
    
    # Nested objects
    products: List[AgreementProductResponse] = []
    store_rules: List[AgreementStoreRuleResponse] = []
    excluded_flags: List[AgreementExcludedFlagResponse] = []

    @field_serializer('start_date', 'end_date')
    def serialize_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date to ISO format."""
        return value.isoformat() if value else None

    model_config = {"from_attributes": True}


class AgreementCreateResponse(BaseModel):
    """Response schema for created agreements."""
    
    id: int
    business_unit_id: Optional[int]
    agreement_number: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    agreement_type_id: Optional[str] = None
    status_id: str
    rebate_type_id: str
    concept_id: str
    description: Optional[str] = None
    activity_name: Optional[str] = None
    source_system: SourceSystemEnum
    spf_code: Optional[str] = None
    spf_description: Optional[str] = None
    currency_id: Optional[int] = None
    unit_price: Decimal
    billing_type: str
    pmm_username: Optional[str] = None
    store_grouping_id: Optional[str] = None
    active: bool
    created_at: str
    created_by_user_email: Optional[str]
    updated_at: str
    updated_status_by_user_email: Optional[str] = None
    
    # Nested objects
    products: List[AgreementProductCreateResponse] = []
    store_rules: List[AgreementStoreRuleCreateResponse] = []
    excluded_flags: List[AgreementExcludedFlagCreateResponse] = []

    @classmethod
    def from_domain_model(cls, agreement_domain_model) -> 'AgreementCreateResponse':
        return cls(
            id=agreement_domain_model.id,
            business_unit_id=agreement_domain_model.business_unit_id,
            agreement_number=agreement_domain_model.agreement_number,
            start_date=agreement_domain_model.start_date,
            end_date=agreement_domain_model.end_date,
            agreement_type_id=agreement_domain_model.agreement_type_id,
            status_id=agreement_domain_model.status_id,
            rebate_type_id=agreement_domain_model.rebate_type_id,
            concept_id=agreement_domain_model.concept_id,
            description=agreement_domain_model.description,
            activity_name=agreement_domain_model.activity_name,
            source_system=agreement_domain_model.source_system,
            spf_code=agreement_domain_model.spf_code,
            spf_description=agreement_domain_model.spf_description,
            currency_id=agreement_domain_model.currency_id,
            unit_price=agreement_domain_model.unit_price,
            billing_type=agreement_domain_model.billing_type,
            pmm_username=agreement_domain_model.pmm_username,
            store_grouping_id=agreement_domain_model.store_grouping_id,
            active=agreement_domain_model.active,
            created_at=agreement_domain_model.created_at,
            created_by_user_email=agreement_domain_model.created_by_user_email,
            updated_at=agreement_domain_model.updated_at,
            updated_status_by_user_email=agreement_domain_model.updated_status_by_user_email,
            products=[
                AgreementProductCreateResponse(
                    id=product.id,
                    agreement_id=product.agreement_id,
                    sku_code=product.sku_code,
                    sku_description=product.sku_description,
                    division_code=product.division_code,
                    division_name=product.division_name,
                    department_code=product.department_code,
                    department_name=product.department_name,
                    subdepartment_code=product.subdepartment_code,
                    subdepartment_name=product.subdepartment_name,
                    class_code=product.class_code,
                    class_name=product.class_name,
                    subclass_code=product.subclass_code,
                    subclass_name=product.subclass_name,
                    brand_id=product.brand_id,
                    brand_name=product.brand_name,
                    supplier_id=product.supplier_id,
                    supplier_name=product.supplier_name,
                    supplier_ruc=product.supplier_ruc,
                    active=product.active,
                    created_at=product.created_at,
                    created_by_user_email=product.created_by_user_email,
                    updated_status_by_user_email=product.updated_status_by_user_email,
                    updated_at=product.updated_at
                ) for product in agreement_domain_model.products
            ],
            store_rules=[
                AgreementStoreRuleCreateResponse(
                    id=rule.id,
                    agreement_id=rule.agreement_id,
                    store_id=rule.store_id,
                    status=rule.status,
                    active=rule.active,
                    created_at=rule.created_at,
                    created_by_user_email=rule.created_by_user_email,
                    updated_status_by_user_email=rule.updated_status_by_user_email,
                    updated_at=rule.updated_at
                ) for rule in agreement_domain_model.store_rules
            ],
            excluded_flags=[
                AgreementExcludedFlagCreateResponse(
                    id=flag.id,
                    agreement_id=flag.agreement_id,
                    excluded_flag_id=flag.excluded_flag_id,
                    active=flag.active,
                    created_at=flag.created_at,
                    created_by_user_email=flag.created_by_user_email,
                    updated_at=flag.updated_at,
                    updated_status_by_user_email=flag.updated_status_by_user_email
                ) for flag in agreement_domain_model.excluded_flags
            ]
        )

    @field_serializer('start_date', 'end_date')
    def serialize_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date to ISO format."""
        return value.isoformat() if value else None


class AgreementCreateSuccessResponse(SuccessResponse[AgreementCreateResponse]):
    """Success response for agreement creation."""
    
    @classmethod
    def from_agreement(cls, agreement: AgreementCreateResponse) -> 'AgreementCreateSuccessResponse':
        return cls(
            success=True,
            message="Agreement created successfully",
            data=agreement
        )


class AgreementSearchResultItem(BaseModel):
    """Schema for individual agreement search results with comprehensive data."""
    
    # Basic agreement information
    id: int
    agreement_number: Optional[int] = None
    description: Optional[str] = None
    source_system: SourceSystemEnum
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: str
    created_by_user_email: str
    updated_at: str
    updated_status_by_user_email: Optional[str] = None
    
    # Status information
    status_id: str
    status_description: Optional[str] = None
    
    # Rebate type information
    rebate_type_id: str
    rebate_type_description: Optional[str] = None
    
    # Concept information
    concept_id: Optional[str] = None
    concept_description: Optional[str] = None
    
    # SPF information
    spf_code: Optional[str] = None
    spf_description: Optional[str] = None
    
    # Financial information
    currency_id: Optional[int] = None
    currency_code: Optional[str] = None
    unit_price: Optional[Decimal] = None
    billing_type: Optional[str] = None
    billing_type_description: Optional[str] = None
    
    # PMM information
    pmm_username: Optional[str] = None
    pmm_username_description: Optional[str] = None
    
    # Store grouping information
    store_grouping_id: Optional[str] = None
    store_grouping_description: Optional[str] = None
    
    # Product information (from first/main product)
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

    @field_serializer('start_date', 'end_date')
    def serialize_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date to ISO format."""
        return value.isoformat() if value else None

    @field_serializer('unit_price')
    def serialize_decimal(self, value: Optional[Decimal]) -> Optional[str]:
        """Serialize decimal to string to avoid precision issues."""
        return str(value) if value is not None else None

    model_config = {"from_attributes": True}


class AgreementSearchResponse(BaseModel):
    """Response schema for agreement search results."""
    
    agreements: List[AgreementSearchResultItem]
    total_count: int

    model_config = {"from_attributes": True}


class AgreementDetailResponse(BaseModel):
    """Detailed response schema for a single agreement with all related data."""
    
    # Basic agreement information
    id: int = Field(..., description="Agreement ID")
    business_unit_id: int = Field(..., description="Business unit ID")
    agreement_number: Optional[int] = Field(None, description="Agreement number")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    agreement_type_id: Optional[str] = Field(None, description="Agreement type ID")
    status_id: str = Field(..., description="Agreement status ID")
    rebate_type_id: str = Field(..., description="Rebate type ID")
    concept_id: str = Field(..., description="Concept ID")
    description: Optional[str] = Field(None, description="Agreement description")
    activity_name: Optional[str] = Field(None, description="Activity name")
    source_system: SourceSystemEnum = Field(..., description="Source system")
    spf_code: Optional[str] = Field(None, description="SPF code")
    spf_description: Optional[str] = Field(None, description="SPF description")
    currency_id: Optional[int] = Field(None, description="Currency ID")
    unit_price: Decimal = Field(..., description="Unit price")
    billing_type: str = Field(..., description="Billing type")
    pmm_username: Optional[str] = Field(None, description="PMM username")
    store_grouping_id: Optional[str] = Field(None, description="Store grouping ID")
    bulk_upload_document_id: Optional[int] = Field(None, description="Bulk upload document ID")
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_at: str = Field(..., description="Last update timestamp")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    
    # Lookup descriptions
    status_description: Optional[str] = Field(None, description="Status description from lookup")
    rebate_type_description: Optional[str] = Field(None, description="Rebate type description from lookup")
    concept_description: Optional[str] = Field(None, description="Concept description from lookup")
    billing_type_description: Optional[str] = Field(None, description="Billing type description from lookup")
    pmm_username_description: Optional[str] = Field(None, description="PMM username description from lookup")
    store_grouping_description: Optional[str] = Field(None, description="Store grouping description from lookup")
    
    # Related data arrays
    products: List[AgreementProductResponse] = Field(
        default_factory=list,
        description="List of agreement products"
    )
    store_rules: List[AgreementStoreRuleResponse] = Field(
        default_factory=list,
        description="List of agreement store rules"
    )
    excluded_flags: List[AgreementExcludedFlagResponse] = Field(
        default_factory=list,
        description="List of agreement excluded flags"
    )

    @field_serializer('start_date', 'end_date')
    def serialize_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date to ISO format."""
        return value.isoformat() if value else None

    @field_serializer('unit_price')
    def serialize_decimal(self, value: Decimal) -> str:
        """Serialize decimal to string to avoid precision issues."""
        return str(value)

    model_config = {
        "from_attributes": True
    }


class AgreementDetailSuccessResponse(SuccessResponse[AgreementDetailResponse]):
    """Success response wrapper for agreement detail."""
    pass

#endregion