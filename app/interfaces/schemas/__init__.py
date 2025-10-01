"""Pydantic schemas for request/response validation."""

from .lookup_schema import LookupCategoryCodeSchema, LookupOptionValueSchema
from .module_schema import (
    ActiveModuleUsersResponse,
    ModuleIdRequest,
    ModuleSchema,
    ModulesResponse,
    ModuleUserSchema,
    ModuleUsersResponse,
)
from ...core.response import (
    BaseResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
    create_error_response,
    create_paginated_response,
    create_success_response,
)
from .stores_schema import StoreResponse
# Agreement schemas separated by domain
from .agreement_schema import (
    # Main agreement schemas
    AgreementSearchRequest,
    AgreementCreateRequest,
    AgreementUpdateRequest,
    AgreementCreateResponse,
    AgreementCreateSuccessResponse,
    AgreementSearchResponse,
    AgreementSearchResultItem,
    AgreementResponse,
)
from .agreement_product_schema import (
    # Product schemas
    AgreementProductCreateRequest,
    AgreementProductCreateResponse,
    AgreementProductResponse,
)
from .agreement_store_rule_schema import (
    # Store rule schemas
    AgreementStoreRuleCreateRequest,
    AgreementStoreRuleCreateResponse,
    AgreementStoreRuleResponse,
)
from .agreement_excluded_flag_schema import (
    # Excluded flag schemas
    AgreementExcludedFlagCreateRequest,
    AgreementExcludedFlagCreateResponse,
    AgreementExcludedFlagResponse,
)
from app.core.validators import UnifiedValidator, validate_secure_string, validate_secure_string_advanced, validate_with_timing_protection 
from .sku_schema import SkuCodesRequest, SkuResponse, SkusResponse

from ...domain.entities.agreement import Agreement
from ...domain.entities.sku import Sku
from ...core.agreement_enums import SourceSystemEnum, StoreRuleStatusEnum
from ...domain.entities.agreement_excluded_flag import AgreementExcludedFlag
from ...domain.entities.agreement_product import AgreementProduct
from ...domain.entities.agreement_store_rule import AgreementStoreRule
from ...domain.entities.division import Division
from ...domain.entities.lookup import LookupValueResult
from ...domain.entities.module import Module
from ...domain.entities.stores import Stores

__all__ = [
    # Lookup schemas
    "LookupCategoryCodeSchema",
    "LookupOptionValueSchema",
    # Module schemas
    "ActiveModuleUsersResponse",
    "ModuleIdRequest",
    "ModuleSchema",
    "ModulesResponse",
    "ModuleUserSchema",
    "ModuleUsersResponse",
    # Response schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
    "create_error_response",
    "create_paginated_response",
    "create_success_response",
    # Store schemas
    "StoreResponse",
    # Agreement schemas (unified)
    "AgreementSearchRequest",
    "AgreementCreateRequest",
    "AgreementUpdateRequest",
    "AgreementProductCreateRequest",
    "AgreementStoreRuleCreateRequest",
    "AgreementExcludedFlagCreateRequest",
    "AgreementCreateResponse",
    "AgreementProductCreateResponse",
    "AgreementStoreRuleCreateResponse",
    "AgreementExcludedFlagCreateResponse",
    "AgreementCreateSuccessResponse",
    "AgreementSearchResponse",
    "AgreementSearchResultItem",
    "AgreementResponse",
    "AgreementProductResponse",
    "AgreementStoreRuleResponse",
    "AgreementExcludedFlagResponse",
    # Validator schemas
    "UnifiedValidator",
    "validate_secure_string",
    "validate_secure_string_advanced",
    "validate_with_timing_protection",
    # SKU schemas
    "SkuCodesRequest",
    "SkuResponse",
    "SkusResponse",
    # Domain entities
    "Agreement",
    "SourceSystemEnum",
    "StoreRuleStatusEnum",
    "AgreementExcludedFlag",
    "AgreementProduct",
    "AgreementStoreRule",
    "Division",
    "LookupValueResult",
    "Module",
    "Stores",
    "Sku",
]
