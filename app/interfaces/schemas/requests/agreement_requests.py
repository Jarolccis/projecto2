"""Agreement request schemas for validation."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.validators import validate_secure_string_advanced
from app.core.agreement_enums import SourceSystemEnum


class AgreementSearchRequest(BaseModel):
    """Schema for agreement search request parameters with business validation."""
    
    # Listas múltiples
    division_codes: Optional[List[str]] = Field(
        None, 
        description="List of division codes to filter by",
        max_length=50
    )
    status_ids: Optional[List[str]] = Field(
        None,
        description="List of status IDs to filter by",
        max_length=50
    )
    created_by_emails: Optional[List[str]] = Field(
        None,
        description="List of creator emails to filter by",
        max_length=20
    )
    
    # Filtros simples
    agreement_number: Optional[int] = Field(
        None,
        ge=1,
        le=999999999,
        description="Agreement number to search for"
    )
    sku_code: Optional[str] = Field(
        None,
        max_length=50,
        description="SKU code to search for (partial match)"
    )
    description: Optional[str] = Field(
        None,
        max_length=70,
        description="Agreement description to search for (partial match)"
    )
    rebate_type_id: Optional[str] = Field(
        None,
        max_length=10,
        description="Rebate type ID to filter by"
    )
    concept_id: Optional[str] = Field(
        None,
        max_length=10,
        description="Concept ID to filter by"
    )
    spf_code: Optional[str] = Field(
        None,
        max_length=50,
        description="SPF code to search for (partial match)"
    )
    spf_description: Optional[str] = Field(
        None,
        max_length=100,
        description="SPF description to search for (partial match)"
    )
    start_date: Optional[date] = Field(
        None,
        description="Filter agreements starting from this date"
    )
    end_date: Optional[date] = Field(
        None,
        description="Filter agreements ending before this date"
    )
    supplier_ruc: Optional[str] = Field(
        None,
        max_length=20,
        description="Supplier RUC to filter by"
    )
    supplier_name: Optional[str] = Field(
        None,
        max_length=160,
        description="Supplier name to search for (partial match)"
    )
    store_grouping_id: Optional[str] = Field(
        None,
        max_length=10,
        description="Store grouping ID to filter by"
    )
    pmm_username: Optional[str] = Field(
        None,
        max_length=10,
        description="PMM username to search for (partial match)"
    )
    
    # Paginación
    limit: Optional[int] = Field(
        None,
        gt=0,
        le=1000,
        description="Maximum number of results to return"
    )
    offset: Optional[int] = Field(
        None,
        ge=0,
        description="Number of results to skip"
    )

    @field_validator('division_codes')
    @classmethod
    def validate_division_codes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate division codes format."""
        if v is None:
            return v
        
        if len(v) > 50:
            raise ValueError("Cannot search more than 50 division codes at once")
        
        for code in v:
            if not code or len(code.strip()) == 0:
                raise ValueError("Division code cannot be empty")
            if len(code) > 10:
                raise ValueError("Division code cannot exceed 10 characters")
            if not code.replace("_", "").replace("-", "").isalnum():
                raise ValueError(f"Invalid division code format: {code}")
        
        return v

    @field_validator('status_ids')
    @classmethod
    def validate_status_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate status IDs format."""
        if v is None:
            return v
        
        if len(v) > 50:
            raise ValueError("Cannot search more than 50 status IDs at once")
        
        for status_id in v:
            if not status_id or len(status_id.strip()) == 0:
                raise ValueError("Status ID cannot be empty")
            if len(status_id) > 10:
                raise ValueError("Status ID cannot exceed 10 characters")
            if not status_id.isalnum():
                raise ValueError(f"Invalid status ID format: {status_id}")
        
        return v

    @field_validator('created_by_emails')
    @classmethod
    def validate_created_by_emails(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate email list format."""
        if v is None:
            return v
        
        if len(v) > 20:
            raise ValueError("Cannot search more than 20 creator emails at once")
        
        for email in v:
            if not email or len(email.strip()) == 0:
                raise ValueError("Email cannot be empty")
            if len(email) > 255:
                raise ValueError("Email cannot exceed 255 characters")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError(f"Invalid email format: {email}")
        
        return v

    @field_validator('sku_code')
    @classmethod
    def validate_sku_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate SKU code with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="SKU code",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)\_\%\@]+$',
            field_name="Description",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate SPF code with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="SPF code",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate SPF description with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)\_\%\@]+$',
            field_name="SPF description",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('supplier_ruc')
    @classmethod
    def validate_supplier_ruc(cls, v: Optional[str]) -> Optional[str]:
        """Validate supplier RUC with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[0-9\-]+$',
            field_name="Supplier RUC",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('supplier_name')
    @classmethod
    def validate_supplier_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate supplier name with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)\_\%\@]+$',
            field_name="Supplier name",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate PMM username with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9_]+$',
            field_name="PMM username",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('rebate_type_id', 'concept_id', 'store_grouping_id')
    @classmethod
    def validate_id_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate ID fields with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9_]+$',
            field_name="ID field",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )

    @model_validator(mode='after')
    def validate_date_range(self) -> 'AgreementSearchRequest':
        """Validate date range constraints."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date cannot be after end date")
        return self


# Create Agreement Request Schemas
class AgreementProductCreateRequest(BaseModel):
    """Schema for agreement product creation request."""
    
    sku_code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="SKU code (1-50 characters)"
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
        max_length=120,
        description="Division name (max 120 characters)"
    )
    department_code: Optional[str] = Field(
        None, 
        max_length=20,
        description="Department code (max 20 characters)"
    )
    department_name: Optional[str] = Field(
        None, 
        max_length=120,
        description="Department name (max 120 characters)"
    )
    subdepartment_code: Optional[str] = Field(
        None, 
        max_length=20,
        description="Subdepartment code (max 20 characters)"
    )
    subdepartment_name: Optional[str] = Field(
        None, 
        max_length=120,
        description="Subdepartment name (max 120 characters)"
    )
    class_code: Optional[str] = Field(
        None, 
        max_length=20,
        description="Class code (max 20 characters)"
    )
    class_name: Optional[str] = Field(
        None, 
        max_length=120,
        description="Class name (max 120 characters)"
    )
    subclass_code: Optional[str] = Field(
        None, 
        max_length=20,
        description="Subclass code (max 20 characters)"
    )
    subclass_name: Optional[str] = Field(
        None, 
        max_length=120,
        description="Subclass name (max 120 characters)"
    )
    brand_id: Optional[str] = Field(
        None, 
        max_length=80,
        description="Brand ID (max 80 characters)"
    )
    brand_name: Optional[str] = Field(
        None, 
        max_length=120,
        description="Brand name (max 120 characters)"
    )
    supplier_id: Optional[int] = Field(
        None, 
        gt=0, 
        le=999999999,
        description="Supplier identifier (1-999999999)"
    )
    supplier_name: Optional[str] = Field(
        None, 
        max_length=160,
        description="Supplier name (max 160 characters)"
    )
    supplier_ruc: Optional[str] = Field(
        None, 
        max_length=20,
        description="Supplier RUC (max 20 characters)"
    )

    @field_validator('sku_code')
    @classmethod
    def validate_sku_code(cls, v: str) -> str:
        """Validate SKU code with security checks."""
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_\.]+$',
            field_name="SKU code",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('supplier_ruc')
    @classmethod
    def validate_supplier_ruc(cls, v: Optional[str]) -> Optional[str]:
        """Validate supplier RUC with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[0-9\-]+$',
            field_name="Supplier RUC",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )


class AgreementStoreRuleCreateRequest(BaseModel):
    """Schema for agreement store rule creation request."""
    
    store_id: int = Field(
        ..., 
        gt=0, 
        le=999999,
        description="Store identifier (1-999999)"
    )
    status: str = Field(
        ...,
        description="Store rule status (INCLUDE/EXCLUDE)"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        if v not in ['INCLUDE', 'EXCLUDE']:
            raise ValueError("Status must be either 'INCLUDE' or 'EXCLUDE'")
        return v


class AgreementExcludedFlagCreateRequest(BaseModel):
    """Schema for agreement excluded flag creation request."""
    
    excluded_flag_id: str = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Excluded flag identifier (1-10 characters)"
    )

    @field_validator('excluded_flag_id')
    @classmethod
    def validate_excluded_flag_id(cls, v: str) -> str:
        """Validate excluded flag ID with security checks."""
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Excluded flag ID",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )


class AgreementCreateRequest(BaseModel):
    """Schema for agreement creation request with all related data."""
    
    business_unit_id: int = Field(
        ..., 
        gt=0, 
        le=999999,
        description="Business unit identifier (1-999999)"
    )
    agreement_number: Optional[int] = Field(
        None, 
        gt=0, 
        le=999999999,
        description="Agreement number (1-999999999)"
    )
    start_date: Optional[date] = Field(
        None,
        description="Agreement start date"
    )
    end_date: Optional[date] = Field(
        None,
        description="Agreement end date"
    )
    agreement_type_id: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=10,
        description="Agreement type identifier (1-10 characters, nullable)"
    )
    status_id: str = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Status identifier (1-10 characters)"
    )
    rebate_type_id: str = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Rebate type identifier (1-10 characters)"
    )
    concept_id: str = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Concept identifier (1-10 characters)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=70,
        description="Agreement description (max 70 characters)"
    )
    activity_name: Optional[str] = Field(
        None, 
        max_length=100,
        description="Activity name (max 100 characters)"
    )
    source_system: SourceSystemEnum = Field(
        ...,
        description="Source system (SPF or PMM)"
    )
    spf_code: Optional[str] = Field(
        None, 
        max_length=50,
        description="SPF code (max 50 characters)"
    )
    spf_description: Optional[str] = Field(
        None, 
        max_length=100,
        description="SPF description (max 100 characters)"
    )
    currency_id: Optional[int] = Field(
        None, 
        gt=0, 
        le=999999,
        description="Currency identifier (1-999999)"
    )
    unit_price: Decimal = Field(
        ..., 
        gt=Decimal('0'), 
        le=Decimal('999999999.99'),
        max_digits=12,
        decimal_places=2,
        description="Unit price (0.01-999999999.99)"
    )
    billing_type: str = Field(
        ..., 
        min_length=1, 
        max_length=10,
        description="Billing type (1-10 characters)"
    )
    pmm_username: Optional[str] = Field(
        None, 
        max_length=10,
        description="PMM username (max 10 characters)"
    )
    store_grouping_id: Optional[str] = Field(
        None, 
        max_length=10,
        description="Store grouping identifier (max 10 characters)"
    )
    products: List[AgreementProductCreateRequest] = Field(
        ...,
        min_items=1,
        max_items=1000,
        description="Agreement products (1-1000 items)"
    )
    store_rules: List[AgreementStoreRuleCreateRequest] = Field(
        default=[],
        min_items=0,
        max_items=10000,
        description="Store rules (0-10000 items)"
    )
    excluded_flags: List[AgreementExcludedFlagCreateRequest] = Field(
        default=[],
        max_items=100,
        description="Excluded flags (max 100 items)"
    )

    @field_validator('agreement_type_id')
    @classmethod
    def validate_agreement_type_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate agreement_type_id field (nullable)."""
        if v is None:
            return None
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="Agreement type ID",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('status_id', 'rebate_type_id', 'concept_id', 'billing_type')
    @classmethod
    def validate_id_fields(cls, v: str) -> str:
        """Validate ID fields with security checks."""
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="ID field",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description with security checks."""
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)]+$',
            field_name="Description",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('activity_name')
    @classmethod
    def validate_activity_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate activity name with security checks."""
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)]+$',
            field_name="Activity name",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('spf_code')
    @classmethod
    def validate_spf_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate SPF code with security checks."""
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9\-_]+$',
            field_name="SPF code",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('spf_description')
    @classmethod
    def validate_spf_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate SPF description with security checks."""
        if v is None:
            return v
        
        if not v.strip():
            return None
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9ñáéíóúüÁÉÍÓÚÜ\s\-\.\,\&\+\#\(\)]+$',
            field_name="SPF description",
            max_repeated_chars=4,
            normalize_whitespace=True,
            to_upper=False
        )

    @field_validator('pmm_username')
    @classmethod
    def validate_pmm_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate PMM username with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9_]+$',
            field_name="PMM username",
            max_repeated_chars=3,
            normalize_whitespace=False,
            to_upper=False
        )

    @field_validator('store_grouping_id')
    @classmethod
    def validate_store_grouping_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate store grouping ID with security checks."""
        if v is None:
            return v
        
        return validate_secure_string_advanced(
            value=v,
            allowed_pattern=r'^[a-zA-Z0-9_]+$',
            field_name="Store grouping ID",
            max_repeated_chars=2,
            normalize_whitespace=False,
            to_upper=False
        )

    @model_validator(mode='after')
    def validate_date_range(self) -> 'AgreementCreateRequest':
        """Validate date range constraints."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date cannot be after end date")
        return self
