from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.response import SuccessResponse
from app.core.agreement_enums import SourceSystemEnum


class AgreementProductCreateResponse(BaseModel):
    
    id: int = Field(..., description="Product ID")
    agreement_id: int = Field(..., description="Agreement ID")
    sku_code: str = Field(..., description="SKU code")
    sku_description: Optional[str] = Field(None, description="SKU description")
    division_code: Optional[str] = Field(None, description="Division code")
    division_name: Optional[str] = Field(None, description="Division name")
    department_code: Optional[str] = Field(None, description="Department code")
    department_name: Optional[str] = Field(None, description="Department name")
    subdepartment_code: Optional[str] = Field(None, description="Subdepartment code")
    subdepartment_name: Optional[str] = Field(None, description="Subdepartment name")
    class_code: Optional[str] = Field(None, description="Class code")
    class_name: Optional[str] = Field(None, description="Class name")
    subclass_code: Optional[str] = Field(None, description="Subclass code")
    subclass_name: Optional[str] = Field(None, description="Subclass name")
    brand_id: Optional[str] = Field(None, description="Brand ID")
    brand_name: Optional[str] = Field(None, description="Brand name")
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    supplier_ruc: Optional[str] = Field(None, description="Supplier RUC")
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    updated_at: str = Field(..., description="Last update timestamp")


class AgreementStoreRuleCreateResponse(BaseModel):
    
    id: int = Field(..., description="Store rule ID")
    agreement_id: int = Field(..., description="Agreement ID")
    store_id: int = Field(..., description="Store ID")
    status: str = Field(..., description="Store rule status")
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    updated_at: str = Field(..., description="Last update timestamp")


class AgreementExcludedFlagCreateResponse(BaseModel):
    
    id: int = Field(..., description="Excluded flag ID")
    agreement_id: int = Field(..., description="Agreement ID")
    excluded_flag_id: str = Field(..., description="Excluded flag identifier")
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_at: str = Field(..., description="Last update timestamp")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")


class AgreementCreateResponse(BaseModel):
    
    id: int = Field(..., description="Agreement ID")
    business_unit_id: int = Field(..., description="Business unit ID")
    agreement_number: Optional[int] = Field(None, description="Agreement number")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    agreement_type_id: Optional[str] = Field(None, description="Agreement type ID")
    status_id: str = Field(..., description="Status ID")
    rebate_type_id: str = Field(..., description="Rebate type ID")
    concept_id: str = Field(..., description="Concept ID")
    description: Optional[str] = Field(None, description="Description")
    activity_name: Optional[str] = Field(None, description="Activity name")
    source_system: SourceSystemEnum = Field(..., description="Source system")
    spf_code: Optional[str] = Field(None, description="SPF code")
    spf_description: Optional[str] = Field(None, description="SPF description")
    currency_id: Optional[int] = Field(None, description="Currency ID")
    unit_price: Decimal = Field(..., description="Unit price")
    billing_type: str = Field(..., description="Billing type")
    pmm_username: Optional[str] = Field(None, description="PMM username")
    store_grouping_id: Optional[str] = Field(None, description="Store grouping ID")
    active: bool = Field(..., description="Active status")
    created_at: str = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_at: str = Field(..., description="Last update timestamp")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    products: List[AgreementProductCreateResponse] = Field(..., description="Agreement products")
    store_rules: List[AgreementStoreRuleCreateResponse] = Field(..., description="Store rules")
    excluded_flags: List[AgreementExcludedFlagCreateResponse] = Field(..., description="Excluded flags")

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


class AgreementCreateSuccessResponse(SuccessResponse[AgreementCreateResponse]):
    """Response for successful agreement creation."""
    
    @classmethod
    def from_agreement_create_response(cls, agreement_response: AgreementCreateResponse) -> 'AgreementCreateSuccessResponse':
        """Create success response from agreement create response."""
        return cls(
            success=True,
            message="Agreement created successfully",
            data=agreement_response
        )


#region Search Response Schemas

class AgreementSearchResultItem(BaseModel):
    """Schema for individual agreement search result."""
    
    # Agreement data
    agreement_id: int = Field(..., description="Agreement ID")
    agreement_number: Optional[int] = Field(None, description="Agreement number")
    status_id: str = Field(..., description="Status ID")
    status_description: Optional[str] = Field(None, description="Status description")
    rebate_type_id: str = Field(..., description="Rebate type ID")
    rebate_type_description: Optional[str] = Field(None, description="Rebate type description")
    concept_id: str = Field(..., description="Concept ID")
    concept_description: Optional[str] = Field(None, description="Concept description")
    agreement_description: Optional[str] = Field(None, description="Agreement description")
    source_system: SourceSystemEnum = Field(..., description="Source system")
    spf_code: Optional[str] = Field(None, description="SPF code")
    spf_description: Optional[str] = Field(None, description="SPF description")
    currency_id: Optional[int] = Field(None, description="Currency ID")
    unit_price: Decimal = Field(..., description="Unit price")
    billing_type: str = Field(..., description="Billing type")
    billing_type_description: Optional[str] = Field(None, description="Billing type description")
    pmm_username: Optional[str] = Field(None, description="PMM username")
    pmm_username_description: Optional[str] = Field(None, description="PMM username description")
    store_grouping_id: Optional[str] = Field(None, description="Store grouping ID")
    store_grouping_description: Optional[str] = Field(None, description="Store grouping description")
    start_date: Optional[date] = Field(None, description="Agreement start date")
    end_date: Optional[date] = Field(None, description="Agreement end date")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by_user_email: str = Field(..., description="Creator email")
    updated_at: datetime = Field(..., description="Last update timestamp")
    updated_status_by_user_email: Optional[str] = Field(None, description="Last updater email")
    
    # Product data
    sku_code: Optional[str] = Field(None, description="SKU code")
    sku_description: Optional[str] = Field(None, description="SKU description")
    division_code: Optional[str] = Field(None, description="Division code")
    division_name: Optional[str] = Field(None, description="Division name")
    department_code: Optional[str] = Field(None, description="Department code")
    department_name: Optional[str] = Field(None, description="Department name")
    subdepartment_code: Optional[str] = Field(None, description="Subdepartment code")
    subdepartment_name: Optional[str] = Field(None, description="Subdepartment name")
    class_code: Optional[str] = Field(None, description="Class code")
    class_name: Optional[str] = Field(None, description="Class name")
    subclass_code: Optional[str] = Field(None, description="Subclass code")
    subclass_name: Optional[str] = Field(None, description="Subclass name")
    brand_id: Optional[str] = Field(None, description="Brand ID")
    brand_name: Optional[str] = Field(None, description="Brand name")
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    supplier_ruc: Optional[str] = Field(None, description="Supplier RUC")
    
    # Currency data
    currency_code: Optional[str] = Field(None, description="Currency code")
    
    model_config = {
        "from_attributes": True
    }


class AgreementSearchResponse(BaseModel):
    """Schema for agreement search response."""
    
    results: List[AgreementSearchResultItem] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results (if known)")

    model_config = {
        "from_attributes": True
    }

#endregion


#region Legacy Response Schemas (from agreement_schema.py)

class AgreementResponse(BaseModel):
    id: int
    business_unit_id: int
    agreement_number: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]
    agreement_type_id: Optional[str]
    status_id: str
    rebate_type_id: str
    concept_id: str
    description: Optional[str]
    activity_name: Optional[str]
    source_system: SourceSystemEnum
    spf_code: Optional[str]
    spf_description: Optional[str]
    currency_id: Optional[int]
    unit_price: Decimal
    billing_type: str
    pmm_username: Optional[str]
    store_grouping_id: Optional[str]
    active: bool
    created_at: str
    created_by_user_email: str
    updated_at: str
    updated_status_by_user_email: Optional[str]
    products: List['AgreementProductResponse']
    store_rules: List['AgreementStoreRuleResponse']
    excluded_flags: List['AgreementExcludedFlagResponse']


class AgreementProductResponse(BaseModel):
    id: int
    agreement_id: int
    sku_code: str
    sku_description: Optional[str]
    division_code: Optional[str]
    division_name: Optional[str]
    department_code: Optional[str]
    department_name: Optional[str]
    subdepartment_code: Optional[str]
    subdepartment_name: Optional[str]
    class_code: Optional[str]
    class_name: Optional[str]
    subclass_code: Optional[str]
    subclass_name: Optional[str]
    brand_id: Optional[str]
    brand_name: Optional[str]
    supplier_id: Optional[int]
    supplier_name: Optional[str]
    supplier_ruc: Optional[str]
    active: bool
    created_at: str
    created_by_user_email: str
    updated_status_by_user_email: Optional[str]
    updated_at: str


class AgreementStoreRuleResponse(BaseModel):
    id: int
    agreement_id: int
    store_id: int
    status: str
    active: bool
    created_at: str
    created_by_user_email: str
    updated_status_by_user_email: Optional[str]
    updated_at: str
    store_name: Optional[str] = None  # Store name from store catalog


class AgreementExcludedFlagResponse(BaseModel):
    id: int
    agreement_id: int
    excluded_flag_id: str
    active: bool
    created_at: str
    created_by_user_email: str
    updated_at: str
    updated_status_by_user_email: Optional[str]
    excluded_flag_name: Optional[str] = None

#endregion
