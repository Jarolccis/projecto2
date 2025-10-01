
from typing import List
from sqlalchemy.engine.row import Row
from app.interfaces.schemas.agreement_schema import AgreementSearchResultItem
from app.interfaces.schemas.agreement_schema import (
    AgreementCreateRequest,
    AgreementUpdateRequest,
    AgreementProductCreateRequest,
    AgreementStoreRuleCreateRequest,
    AgreementExcludedFlagCreateRequest
)
from app.interfaces.schemas import (
    AgreementResponse,
    AgreementProductResponse,
    AgreementStoreRuleResponse,
    AgreementExcludedFlagResponse
)
from app.domain.entities.agreement import Agreement
from app.domain.entities.agreement_product import AgreementProduct
from app.domain.entities.agreement_store_rule import AgreementStoreRule
from app.domain.entities.agreement_excluded_flag import AgreementExcludedFlag
import logging

logger = logging.getLogger(__name__)


def map_search_result_to_agreement_item(row: Row) -> AgreementSearchResultItem:
    """
    Map PostgreSQL function result to AgreementSearchResultItem.
    
    This function maps all fields returned by the search_agreements PostgreSQL function
    including agreement details, status descriptions, product information, and supplier data.
    """
    try:
        return AgreementSearchResultItem(
            # Basic agreement information
            id=row.agreement_id,
            agreement_number=row.agreement_number,
            description=row.agreement_description,
            source_system=row.source_system,
            start_date=row.start_date,
            end_date=row.end_date,
            created_at=row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at),
            created_by_user_email=row.created_by_user_email or "",
            updated_at=row.updated_at.isoformat() if hasattr(row.updated_at, 'isoformat') else str(row.updated_at),
            updated_status_by_user_email=row.updated_status_by_user_email,
            
            # Status information
            status_id=row.status_id or "",
            status_description=row.status_description,
            
            # Rebate type information
            rebate_type_id=row.rebate_type_id or "",
            rebate_type_description=row.rebate_type_description,
            
            # Concept information
            concept_id=row.concept_id,
            concept_description=row.concept_description,
            
            # SPF information
            spf_code=row.spf_code,
            spf_description=row.spf_description,
            
            # Financial information
            currency_id=row.currency_id,
            currency_code=row.currency_code,
            unit_price=row.unit_price,
            billing_type=row.billing_type,
            billing_type_description=row.billing_type_description,
            
            # PMM information
            pmm_username=row.pmm_username,
            pmm_username_description=row.pmm_username_description,
            
            # Store grouping information
            store_grouping_id=row.store_grouping_id,
            store_grouping_description=row.store_grouping_description,
            
            # Product information
            sku_code=row.sku_code,
            sku_description=row.sku_description,
            division_code=row.division_code,
            division_name=row.division_name,
            department_code=row.department_code,
            department_name=row.department_name,
            subdepartment_code=row.subdepartment_code,
            subdepartment_name=row.subdepartment_name,
            class_code=row.class_code,
            class_name=row.class_name,
            subclass_code=row.subclass_code,
            subclass_name=row.subclass_name,
            brand_id=row.brand_id,
            brand_name=row.brand_name,
            supplier_id=row.supplier_id,
            supplier_name=row.supplier_name,
            supplier_ruc=row.supplier_ruc,
        )
    except AttributeError as e:
        logger.error(f"Missing required column in database row: {e}")
        raise AttributeError(f"Missing required column in database row: {e}")
    except (ValueError, TypeError) as e:
        logger.error(f"Data type conversion error: {e}")
        raise ValueError(f"Data type conversion error: {e}")


def map_search_results_to_agreement_items(rows: list[Row]) -> list[AgreementSearchResultItem]:
    return [map_search_result_to_agreement_item(row) for row in rows]


def map_request_to_agreement_product(request: AgreementProductCreateRequest, agreement_id: int) -> AgreementProduct:
    try:
        return AgreementProduct(
            id=None,  
            agreement_id=agreement_id,
            sku_code=request.sku_code,
            sku_description=request.sku_description,
            division_code=request.division_code,
            division_name=request.division_name,
            department_code=request.department_code,
            department_name=request.department_name,
            subdepartment_code=request.subdepartment_code,
            subdepartment_name=request.subdepartment_name,
            class_code=request.class_code,
            class_name=request.class_name,
            subclass_code=request.subclass_code,
            subclass_name=request.subclass_name,
            brand_id=request.brand_id,
            brand_name=request.brand_name,
            supplier_id=request.supplier_id,
            supplier_name=request.supplier_name,
            supplier_ruc=request.supplier_ruc,
            active=True,
            created_at=None,  
            created_by_user_email=None,  
            updated_status_by_user_email=None,
            updated_at=None  
        )
    except Exception as e:
        logger.error(f"Error mapping agreement product request to domain entity: {e}")
        raise ValueError(f"Failed to map agreement product: {e}")


def map_request_to_agreement_store_rule(request: AgreementStoreRuleCreateRequest, agreement_id: int) -> AgreementStoreRule:
    try:
        return AgreementStoreRule(
            id=None, 
            agreement_id=agreement_id,
            store_id=request.store_id,
            status=request.status,
            active=True,
            created_at=None,  
            created_by_user_email=None, 
            updated_status_by_user_email=None,
            updated_at=None  
        )
    except Exception as e:
        logger.error(f"Error mapping agreement store rule request to domain entity: {e}")
        raise ValueError(f"Failed to map agreement store rule: {e}")


def map_request_to_agreement_excluded_flag(request: AgreementExcludedFlagCreateRequest, agreement_id: int) -> AgreementExcludedFlag:
    try:
        return AgreementExcludedFlag(
            id=None,  
            agreement_id=agreement_id,
            excluded_flag_id=request.excluded_flag_id,
            active=True,
            created_at=None,  
            created_by_user_email=None,  
            updated_at=None,  
            updated_status_by_user_email=None
        )
    except Exception as e:
        logger.error(f"Error mapping agreement excluded flag request to domain entity: {e}")
        raise ValueError(f"Failed to map agreement excluded flag: {e}")


def map_request_to_agreement(request: AgreementCreateRequest) -> Agreement:
    try:
        agreement = Agreement.create(
            business_unit_id=request.business_unit_id,
            agreement_type_id=request.agreement_type_id,
            status_id=request.status_id,
            rebate_type_id=request.rebate_type_id,
            concept_id=request.concept_id,
            source_system=request.source_system,
            unit_price=request.unit_price,
            billing_type=request.billing_type,
            created_by_user_email="", 
            agreement_number=request.agreement_number,
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
            activity_name=request.activity_name,
            spf_code=request.spf_code,
            spf_description=request.spf_description,
            currency_id=request.currency_id,
            pmm_username=request.pmm_username,
            store_grouping_id=request.store_grouping_id,
        )
        
        return agreement
        
    except Exception as e:
        logger.error(f"Error mapping agreement creation request to domain entity: {e}")
        raise ValueError(f"Failed to map agreement creation request: {e}")


def map_update_request_to_agreement(request: AgreementUpdateRequest) -> Agreement:
    """Map AgreementUpdateRequest to Agreement domain entity."""
    try:
        agreement = Agreement.create(
            business_unit_id=request.business_unit_id,
            agreement_type_id=request.agreement_type_id,
            status_id=request.status_id,
            rebate_type_id=request.rebate_type_id,
            concept_id=request.concept_id,
            source_system=request.source_system,
            unit_price=request.unit_price,
            billing_type=request.billing_type,
            created_by_user_email="",  # Will be set by use case
            start_date=request.start_date,
            end_date=request.end_date,
            description=request.description,
            activity_name=request.activity_name,
            spf_code=request.spf_code,
            spf_description=request.spf_description,
            currency_id=request.currency_id,
            pmm_username=request.pmm_username,
            store_grouping_id=request.store_grouping_id,
        )
        
        return agreement
        
    except Exception as e:
        logger.error(f"Error mapping agreement update request to domain entity: {e}")
        raise ValueError(f"Failed to map agreement update request: {e}")


def map_requests_to_agreement_products(requests: List[AgreementProductCreateRequest], agreement_id: int) -> List[AgreementProduct]:
    return [map_request_to_agreement_product(req, agreement_id) for req in requests]


def map_requests_to_agreement_store_rules(requests: List[AgreementStoreRuleCreateRequest], agreement_id: int) -> List[AgreementStoreRule]:
    return [map_request_to_agreement_store_rule(req, agreement_id) for req in requests]


def map_requests_to_agreement_excluded_flags(requests: List[AgreementExcludedFlagCreateRequest], agreement_id: int) -> List[AgreementExcludedFlag]:
    return [map_request_to_agreement_excluded_flag(req, agreement_id) for req in requests]


# ==================== ENTITY TO RESPONSE MAPPERS ====================

def map_agreement_to_response(agreement: Agreement) -> AgreementResponse:
    """Map Agreement domain entity to AgreementResponse."""
    try:
        return AgreementResponse(
            id=agreement.id,
            business_unit_id=agreement.business_unit_id,
            agreement_number=agreement.agreement_number,
            start_date=agreement.start_date,
            end_date=agreement.end_date,
            agreement_type_id=agreement.agreement_type_id,
            status_id=agreement.status_id,
            rebate_type_id=agreement.rebate_type_id,
            concept_id=agreement.concept_id,
            description=agreement.description,
            activity_name=agreement.activity_name,
            source_system=agreement.source_system,
            spf_code=agreement.spf_code,
            spf_description=agreement.spf_description,
            currency_id=agreement.currency_id,
            unit_price=agreement.unit_price,
            billing_type=agreement.billing_type,
            pmm_username=agreement.pmm_username,
            store_grouping_id=agreement.store_grouping_id,
            bulk_upload_document_id=agreement.bulk_upload_document_id,
            active=agreement.active,
            created_at=agreement.created_at.isoformat() if agreement.created_at else None,
            created_by_user_email=agreement.created_by_user_email,
            updated_at=agreement.updated_at.isoformat() if agreement.updated_at else None,
            updated_status_by_user_email=agreement.updated_status_by_user_email,
            # Add lookup descriptions
            status_description=agreement.status_description,
            rebate_type_description=agreement.rebate_type_description,
            concept_description=agreement.concept_description,
            billing_type_description=agreement.billing_type_description,
            pmm_username_description=agreement.pmm_username_description,
            store_grouping_description=agreement.store_grouping_description
        )
    except Exception as e:
        logger.error(f"Error mapping agreement entity to response: {e}")
        raise ValueError(f"Failed to map agreement to response: {e}")


def map_product_to_response(product: AgreementProduct) -> AgreementProductResponse:
    """Map AgreementProduct domain entity to AgreementProductResponse."""
    try:
        return AgreementProductResponse(
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
            created_at=product.created_at.isoformat() if product.created_at else None,
            created_by_user_email=product.created_by_user_email,
            updated_at=product.updated_at.isoformat() if product.updated_at else None,
            updated_status_by_user_email=product.updated_status_by_user_email
        )
    except Exception as e:
        logger.error(f"Error mapping agreement product entity to response: {e}")
        raise ValueError(f"Failed to map agreement product to response: {e}")


def map_store_rule_to_response(store_rule: AgreementStoreRule) -> AgreementStoreRuleResponse:
    """Map AgreementStoreRule domain entity to AgreementStoreRuleResponse."""
    try:
        return AgreementStoreRuleResponse(
            id=store_rule.id,
            agreement_id=store_rule.agreement_id,
            store_id=store_rule.store_id,
            status=store_rule.status,
            active=store_rule.active,
            created_at=store_rule.created_at.isoformat() if store_rule.created_at else None,
            created_by_user_email=store_rule.created_by_user_email,
            updated_at=store_rule.updated_at.isoformat() if store_rule.updated_at else None,
            updated_status_by_user_email=store_rule.updated_status_by_user_email,
            store_name=store_rule.store_name  # Include store name from domain entity
        )
    except Exception as e:
        logger.error(f"Error mapping agreement store rule entity to response: {e}")
        raise ValueError(f"Failed to map agreement store rule to response: {e}")


def map_excluded_flag_to_response(excluded_flag: AgreementExcludedFlag) -> AgreementExcludedFlagResponse:
    """Map AgreementExcludedFlag domain entity to AgreementExcludedFlagResponse."""
    try:
        return AgreementExcludedFlagResponse(
            id=excluded_flag.id,
            agreement_id=excluded_flag.agreement_id,
            excluded_flag_id=excluded_flag.excluded_flag_id,
            active=excluded_flag.active,
            created_at=excluded_flag.created_at.isoformat() if excluded_flag.created_at else None,
            created_by_user_email=excluded_flag.created_by_user_email,
            updated_at=excluded_flag.updated_at.isoformat() if excluded_flag.updated_at else None,
            updated_status_by_user_email=excluded_flag.updated_status_by_user_email,
            excluded_flag_name=excluded_flag.excluded_flag_name
        )
    except Exception as e:
        logger.error(f"Error mapping agreement excluded flag entity to response: {e}")
        raise ValueError(f"Failed to map agreement excluded flag to response: {e}")


def map_products_to_response(products: List[AgreementProduct]) -> List[AgreementProductResponse]:
    """Map list of AgreementProduct entities to list of AgreementProductResponse."""
    return [map_product_to_response(product) for product in products]


def map_store_rules_to_response(store_rules: List[AgreementStoreRule]) -> List[AgreementStoreRuleResponse]:
    """Map list of AgreementStoreRule entities to list of AgreementStoreRuleResponse."""
    return [map_store_rule_to_response(store_rule) for store_rule in store_rules]


def map_excluded_flags_to_response(excluded_flags: List[AgreementExcludedFlag]) -> List[AgreementExcludedFlagResponse]:
    """Map list of AgreementExcludedFlag entities to list of AgreementExcludedFlagResponse."""
    return [map_excluded_flag_to_response(excluded_flag) for excluded_flag in excluded_flags]
