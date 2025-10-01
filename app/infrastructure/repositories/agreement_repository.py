from sqlalchemy import select, and_, text, outerjoin, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from typing import List, Dict, Any, Tuple, Optional
import logging

from app.interfaces.schemas.__init__ import Agreement, AgreementProduct, AgreementStoreRule, AgreementExcludedFlag
from app.core.agreement_enums import SourceSystemEnum, StoreRuleStatusEnum
from app.core.constants import (
    AGREEMENT_STATUSES_CATEGORY, REBATE_TYPE_CATEGORY, CONCEPT_CATEGORY,
    BILLING_TYPE_CATEGORY, PMM_USER_NAME_CATEGORY, STORE_GROUPING_CATEGORY
)
from app.domain.repositories import AgreementRepository
from app.interfaces.schemas.agreement_schema import AgreementSearchRequest, AgreementSearchResponse, AgreementSearchResultItem
from app.infrastructure.postgres.models.tottus.agreement_model import AgreementModel
from app.infrastructure.postgres.models.tottus.agreement_product_model import AgreementProductModel
from app.infrastructure.postgres.models.tottus.agreement_store_rule_model import AgreementStoreRuleModel
from app.infrastructure.postgres.models.tottus.agreement_excluded_flag_model import AgreementExcludedFlagModel
from app.infrastructure.postgres.models.tottus.lookup_category_model import LookupCategoryModel
from app.infrastructure.postgres.models.tottus.lookup_value_model import LookupValueModel
from app.infrastructure.postgres.querys import load_sql_query
from app.infrastructure.mappers import map_search_results_to_agreement_items
from app.infrastructure.repositories.agreement_product_repository import PostgresAgreementProductRepository
from app.infrastructure.repositories.agreement_store_rule_repository import PostgresAgreementStoreRuleRepository
from app.infrastructure.repositories.agreement_excluded_flag_repository import PostgresAgreementExcludedFlagRepository
from app.utils.hashing import format_array

logger = logging.getLogger(__name__)
 

class PostgresAgreementRepository(AgreementRepository):

    def __init__(self, session: AsyncSession):
        self._session = session
        self._product_repository = PostgresAgreementProductRepository(session)
        self._store_rule_repository = PostgresAgreementStoreRuleRepository(session)
        self._excluded_flag_repository = PostgresAgreementExcludedFlagRepository(session)

# ==================== AGREEMENT OPERATIONS ====================

    async def create_agreement(self, agreement: Agreement) -> Agreement:
        agreement_model = AgreementModel(
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
            active=agreement.active,
            created_by_user_email=agreement.created_by_user_email,
            updated_status_by_user_email=agreement.updated_status_by_user_email,
        )
        
        self._session.add(agreement_model)
        await self._session.flush()
        await self._session.refresh(agreement_model)
        
        agreement.id = agreement_model.id
        agreement.created_at = agreement_model.created_at
        agreement.updated_at = agreement_model.updated_at
        
        return agreement

    async def exists_agreement_by_number_and_business_unit(
        self, 
        agreement_number: int, 
        business_unit_id: int
    ) -> bool:
        """Check if an agreement exists by number and business unit."""
        stmt = select(AgreementModel.id).where(
            and_(
                AgreementModel.agreement_number == agreement_number,
                AgreementModel.business_unit_id == business_unit_id,
                AgreementModel.active == True
            )
        )
        
        result = await self._session.execute(stmt)
        scalar_result = result.scalar_one_or_none()
        return scalar_result is not None

    async def get_agreement_by_id(self, agreement_id: int) -> Optional[Agreement]:
        """Get agreement by ID with lookup descriptions."""
        try:
            # Create aliases for each lookup join
            lc_status = LookupCategoryModel.__table__.alias('lc_status')
            lv_status = LookupValueModel.__table__.alias('lv_status')
            
            lc_rebate = LookupCategoryModel.__table__.alias('lc_rebate')
            lv_rebate = LookupValueModel.__table__.alias('lv_rebate')
            
            lc_concept = LookupCategoryModel.__table__.alias('lc_concept')
            lv_concept = LookupValueModel.__table__.alias('lv_concept')
            
            lc_billing = LookupCategoryModel.__table__.alias('lc_billing')
            lv_billing = LookupValueModel.__table__.alias('lv_billing')
            
            lc_pmm = LookupCategoryModel.__table__.alias('lc_pmm')
            lv_pmm = LookupValueModel.__table__.alias('lv_pmm')
            
            lc_store = LookupCategoryModel.__table__.alias('lc_store')
            lv_store = LookupValueModel.__table__.alias('lv_store')
            
            # Build ORM query with lookup joins
            stmt = select(
                AgreementModel.id,
                AgreementModel.business_unit_id,
                AgreementModel.agreement_number,
                AgreementModel.start_date,
                AgreementModel.end_date,
                AgreementModel.agreement_type_id,
                AgreementModel.status_id,
                AgreementModel.rebate_type_id,
                AgreementModel.concept_id,
                AgreementModel.description,
                AgreementModel.activity_name,
                AgreementModel.source_system,
                AgreementModel.spf_code,
                AgreementModel.spf_description,
                AgreementModel.currency_id,
                AgreementModel.unit_price,
                AgreementModel.billing_type,
                AgreementModel.pmm_username,
                AgreementModel.store_grouping_id,
                AgreementModel.bulk_upload_document_id,
                AgreementModel.active,
                AgreementModel.created_at,
                AgreementModel.created_by_user_email,
                AgreementModel.updated_at,
                AgreementModel.updated_status_by_user_email,
                # Lookup descriptions
                lv_status.c.display_value.label('status_description'),
                lv_rebate.c.display_value.label('rebate_type_description'),
                lv_concept.c.display_value.label('concept_description'),
                lv_billing.c.display_value.label('billing_type_description'),
                lv_pmm.c.display_value.label('pmm_username_description'),
                lv_store.c.display_value.label('store_grouping_description')
            ).select_from(
                AgreementModel.__table__
                # Status lookup
                .outerjoin(lc_status, lc_status.c.code == AGREEMENT_STATUSES_CATEGORY)
                .outerjoin(lv_status, and_(
                    lv_status.c.category_id == lc_status.c.id,
                    lv_status.c.option_value == AgreementModel.status_id
                ))
                # Rebate type lookup  
                .outerjoin(lc_rebate, lc_rebate.c.code == REBATE_TYPE_CATEGORY)
                .outerjoin(lv_rebate, and_(
                    lv_rebate.c.category_id == lc_rebate.c.id,
                    lv_rebate.c.option_value == AgreementModel.rebate_type_id
                ))
                # Concept lookup
                .outerjoin(lc_concept, lc_concept.c.code == CONCEPT_CATEGORY)
                .outerjoin(lv_concept, and_(
                    lv_concept.c.category_id == lc_concept.c.id,
                    lv_concept.c.option_value == AgreementModel.concept_id
                ))
                # Billing type lookup
                .outerjoin(lc_billing, lc_billing.c.code == BILLING_TYPE_CATEGORY)
                .outerjoin(lv_billing, and_(
                    lv_billing.c.category_id == lc_billing.c.id,
                    lv_billing.c.option_value == AgreementModel.billing_type
                ))
                # PMM username lookup
                .outerjoin(lc_pmm, lc_pmm.c.code == PMM_USER_NAME_CATEGORY)
                .outerjoin(lv_pmm, and_(
                    lv_pmm.c.category_id == lc_pmm.c.id,
                    lv_pmm.c.option_value == AgreementModel.pmm_username
                ))
                # Store grouping lookup
                .outerjoin(lc_store, lc_store.c.code == STORE_GROUPING_CATEGORY)
                .outerjoin(lv_store, and_(
                    lv_store.c.category_id == lc_store.c.id,
                    lv_store.c.option_value == AgreementModel.store_grouping_id
                ))
            ).where(
                and_(
                    AgreementModel.id == agreement_id,
                    AgreementModel.active == True
                )
            )
            
            result = await self._session.execute(stmt)
            row = result.fetchone()
            
            if row is None:
                logger.info(f"Agreement with ID {agreement_id} not found")
                return None
            
            # Convert row to domain entity
            agreement = Agreement(
                id=row.id,
                business_unit_id=row.business_unit_id,
                agreement_number=row.agreement_number,
                start_date=row.start_date,
                end_date=row.end_date,
                agreement_type_id=row.agreement_type_id,
                status_id=row.status_id,
                rebate_type_id=row.rebate_type_id,
                concept_id=row.concept_id,
                description=row.description,
                activity_name=row.activity_name,
                source_system=row.source_system,
                spf_code=row.spf_code,
                spf_description=row.spf_description,
                currency_id=row.currency_id,
                unit_price=row.unit_price,
                billing_type=row.billing_type,
                pmm_username=row.pmm_username,
                store_grouping_id=row.store_grouping_id,
                bulk_upload_document_id=row.bulk_upload_document_id,
                active=row.active,
                created_at=row.created_at,
                created_by_user_email=row.created_by_user_email,
                updated_at=row.updated_at,
                updated_status_by_user_email=row.updated_status_by_user_email,
                # Add lookup descriptions
                status_description=row.status_description,
                rebate_type_description=row.rebate_type_description,
                concept_description=row.concept_description,
                billing_type_description=row.billing_type_description,
                pmm_username_description=row.pmm_username_description,
                store_grouping_description=row.store_grouping_description
            )
            
            logger.info(f"Agreement {agreement_id} retrieved successfully with lookup descriptions")
            return agreement
            
        except Exception as e:
            logger.error(f"Error retrieving agreement {agreement_id}: {str(e)}")
            raise

    async def get_agreement_with_details(self, agreement_id: int) -> Optional[Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]]:
        """Get agreement by ID with all related data (products, store rules, excluded flags)."""
        try:
            # Get the main agreement
            agreement = await self.get_agreement_by_id(agreement_id)
            if agreement is None:
                return None
            
            # Get all related data in parallel for better performance
            products = await self._product_repository.get_agreement_products(agreement_id)
            store_rules = await self._store_rule_repository.get_agreement_store_rules(agreement_id)
            excluded_flags = await self._excluded_flag_repository.get_agreement_excluded_flags(agreement_id)
            
            logger.info(
                f"Agreement {agreement_id} retrieved with details successfully",
                products_count=len(products),
                store_rules_count=len(store_rules),
                excluded_flags_count=len(excluded_flags)
            )
            
            return agreement, products, store_rules, excluded_flags
            
        except Exception as e:
            logger.error(f"Error retrieving agreement {agreement_id} with details: {str(e)}")
            raise

    async def create_agreement_product(self, product: AgreementProduct) -> AgreementProduct:
        return await self._product_repository.create_agreement_product(product)

    async def create_agreement_store_rule(self, store_rule: AgreementStoreRule) -> AgreementStoreRule:
        return await self._store_rule_repository.create_agreement_store_rule(store_rule)

    async def create_agreement_excluded_flag(self, excluded_flag: AgreementExcludedFlag) -> AgreementExcludedFlag:
        return await self._excluded_flag_repository.create_agreement_excluded_flag(excluded_flag)

    async def create_complete_agreement(
        self,
        agreement: Agreement,
        products: List[AgreementProduct],
        store_rules: List[AgreementStoreRule],
        excluded_flags: List[AgreementExcludedFlag]
    ) -> Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]:
        try:
            created_agreement = await self.create_agreement(agreement)
            
            created_products = []
            for product in products:
                product.agreement_id = created_agreement.id
                created_product = await self._product_repository.create_agreement_product(product)
                created_products.append(created_product)
            
            created_store_rules = []
            for store_rule in store_rules:
                store_rule.agreement_id = created_agreement.id
                created_store_rule = await self._store_rule_repository.create_agreement_store_rule(store_rule)
                created_store_rules.append(created_store_rule)
            
            created_excluded_flags = []
            for excluded_flag in excluded_flags:
                excluded_flag.agreement_id = created_agreement.id
                created_excluded_flag = await self._excluded_flag_repository.create_agreement_excluded_flag(excluded_flag)
                created_excluded_flags.append(created_excluded_flag)

            await self._session.flush()
                        
            logger.info(
                "Complete agreement created successfully",
                agreement_id=created_agreement.id,
                products_count=len(created_products),
                store_rules_count=len(created_store_rules),
                excluded_flags_count=len(created_excluded_flags)
            )
            
            return created_agreement, created_products, created_store_rules, created_excluded_flags
            
        except Exception as e:
            logger.error(
                f"Failed to create complete agreement: {e}",
                extra={"agreement_id": agreement.id}
            )
            raise

    async def update_complete_agreement(
        self,
        agreement_id: int,
        agreement: Agreement,
        products: List[AgreementProduct],
        store_rules: List[AgreementStoreRule],
        excluded_flags: List[AgreementExcludedFlag]
    ) -> Tuple[Agreement, List[AgreementProduct], List[AgreementStoreRule], List[AgreementExcludedFlag]]:
        """Update a complete agreement by replacing all related data."""
        try:
            logger.info(
                "Starting complete agreement update",
                agreement_id=agreement_id,
                products_count=len(products),
                store_rules_count=len(store_rules),
                excluded_flags_count=len(excluded_flags)
            )
            
            # 1. Update the main agreement
            agreement.id = agreement_id
            updated_agreement = await self._update_agreement(agreement)
            
            # 2. Delete all existing related data
            await self._delete_agreement_products(agreement_id)
            await self._delete_agreement_store_rules(agreement_id)
            await self._delete_agreement_excluded_flags(agreement_id)
            
            # 3. Create new related data using direct table operations
            created_products = await self._create_agreement_products_bulk(agreement_id, products)
            created_store_rules = await self._create_agreement_store_rules_bulk(agreement_id, store_rules)
            created_excluded_flags = await self._create_agreement_excluded_flags_bulk(agreement_id, excluded_flags)
                        
            logger.info(
                "Complete agreement updated successfully",
                agreement_id=agreement_id,
                products_count=len(created_products),
                store_rules_count=len(created_store_rules),
                excluded_flags_count=len(created_excluded_flags)
            )
            
            return updated_agreement, created_products, created_store_rules, created_excluded_flags
            
        except Exception as e:
            logger.error(
                f"Failed to update complete agreement: {e}",
                extra={"agreement_id": agreement_id}
            )
            raise

    async def _update_agreement(self, agreement: Agreement) -> Agreement:
        """Update the main agreement data."""
        try:
            # Get the existing agreement first to preserve certain fields
            stmt = select(AgreementModel).where(AgreementModel.id == agreement.id)
            result = await self._session.execute(stmt)
            existing_agreement_model = result.scalars().first()
            
            if not existing_agreement_model:
                raise ValueError(f"Agreement with ID {agreement.id} not found")
            
            # Update the agreement model with new data
            existing_agreement_model.start_date = agreement.start_date
            existing_agreement_model.end_date = agreement.end_date
            existing_agreement_model.agreement_type_id = agreement.agreement_type_id
            existing_agreement_model.status_id = agreement.status_id
            existing_agreement_model.rebate_type_id = agreement.rebate_type_id
            existing_agreement_model.concept_id = agreement.concept_id
            existing_agreement_model.description = agreement.description
            existing_agreement_model.activity_name = agreement.activity_name
            existing_agreement_model.source_system = agreement.source_system
            existing_agreement_model.spf_code = agreement.spf_code
            existing_agreement_model.spf_description = agreement.spf_description
            # existing_agreement_model.currency_id = agreement.currency_id
            existing_agreement_model.unit_price = agreement.unit_price
            existing_agreement_model.billing_type = agreement.billing_type
            existing_agreement_model.pmm_username = agreement.pmm_username
            existing_agreement_model.store_grouping_id = agreement.store_grouping_id
            existing_agreement_model.updated_status_by_user_email = agreement.updated_status_by_user_email
            
            # await self._session.flush()
            # await self._session.refresh(existing_agreement_model)
            
            # Convert back to domain entity using the updated values
            from datetime import datetime
            updated_agreement = Agreement(
                id=existing_agreement_model.id,
                business_unit_id=existing_agreement_model.business_unit_id,
                agreement_number=existing_agreement_model.agreement_number,
                start_date=existing_agreement_model.start_date,
                end_date=existing_agreement_model.end_date,
                agreement_type_id=existing_agreement_model.agreement_type_id,
                status_id=existing_agreement_model.status_id,
                rebate_type_id=existing_agreement_model.rebate_type_id,
                concept_id=existing_agreement_model.concept_id,
                description=existing_agreement_model.description,
                activity_name=existing_agreement_model.activity_name,
                source_system=existing_agreement_model.source_system,
                spf_code=existing_agreement_model.spf_code,
                spf_description=existing_agreement_model.spf_description,
                currency_id=existing_agreement_model.currency_id,
                unit_price=existing_agreement_model.unit_price,
                billing_type=existing_agreement_model.billing_type,
                pmm_username=existing_agreement_model.pmm_username,
                store_grouping_id=existing_agreement_model.store_grouping_id,
                bulk_upload_document_id=existing_agreement_model.bulk_upload_document_id,
                active=existing_agreement_model.active,
                created_at=existing_agreement_model.created_at,
                created_by_user_email=existing_agreement_model.created_by_user_email,
                updated_at=existing_agreement_model.updated_at,
                updated_status_by_user_email=existing_agreement_model.updated_status_by_user_email
            )
            
            logger.info(f"Agreement {agreement.id} updated successfully")
            return updated_agreement
            
        except Exception as e:
            # Remove rollback here - let the outer transaction handle it
            logger.error(f"Failed to update agreement {agreement.id}: {e}")
            raise

    async def _delete_agreement_products(self, agreement_id: int) -> None:
        """Delete all products for an agreement using bulk delete."""
        try:
            # Use direct DELETE statement for better performance
            stmt = delete(AgreementProductModel).where(AgreementProductModel.agreement_id == agreement_id)
            result = await self._session.execute(stmt)
            deleted_count = result.rowcount
            
            logger.info(f"Deleted {deleted_count} products for agreement {agreement_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete products for agreement {agreement_id}: {e}")
            raise

    async def _delete_agreement_store_rules(self, agreement_id: int) -> None:
        """Delete all store rules for an agreement using bulk delete."""
        try:
            # Use direct DELETE statement for better performance
            stmt = delete(AgreementStoreRuleModel).where(AgreementStoreRuleModel.agreement_id == agreement_id)
            result = await self._session.execute(stmt)
            deleted_count = result.rowcount
            
            logger.info(f"Deleted {deleted_count} store rules for agreement {agreement_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete store rules for agreement {agreement_id}: {e}")
            raise

    async def _delete_agreement_excluded_flags(self, agreement_id: int) -> None:
        """Delete all excluded flags for an agreement using bulk delete."""
        try:
            # Use direct DELETE statement for better performance
            stmt = delete(AgreementExcludedFlagModel).where(AgreementExcludedFlagModel.agreement_id == agreement_id)
            result = await self._session.execute(stmt)
            deleted_count = result.rowcount
            
            logger.info(f"Deleted {deleted_count} excluded flags for agreement {agreement_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete excluded flags for agreement {agreement_id}: {e}")
            raise

    async def _create_agreement_products_bulk(self, agreement_id: int, products: List[AgreementProduct]) -> List[AgreementProduct]:
        """Create multiple agreement products using bulk insert."""
        try:
            if not products:
                return []
            
            # Prepare data for bulk insert
            products_data = []
            for product in products:
                products_data.append({
                    'agreement_id': agreement_id,
                    'sku_code': product.sku_code,
                    'sku_description': product.sku_description,
                    'supplier_ruc': product.supplier_ruc,
                    'supplier_name': product.supplier_name,
                    'division_code': product.division_code,
                    'division_name': product.division_name,
                    'department_code': product.department_code,
                    'department_name': product.department_name,
                    'subdepartment_code': product.subdepartment_code,
                    'subdepartment_name': product.subdepartment_name,
                    'class_code': product.class_code,
                    'class_name': product.class_name,
                    'subclass_code': product.subclass_code,
                    'subclass_name': product.subclass_name,
                    'brand_id': product.brand_id,
                    'brand_name': product.brand_name,
                    'supplier_id': product.supplier_id,
                    'active': product.active,
                    'created_by_user_email': product.created_by_user_email,
                    'updated_status_by_user_email': product.updated_status_by_user_email
                })
            
            # Execute bulk insert
            stmt = AgreementProductModel.__table__.insert().values(products_data)
            result = await self._session.execute(stmt)
            
            # Instead of querying back, return domain entities with estimated data
            # This saves a SELECT query and improves performance significantly
            created_products = []
            for i, product in enumerate(products):
                # Create domain entity with original data (IDs will be assigned by DB)
                created_product = AgreementProduct(
                    id=None,  # Will be assigned by database
                    agreement_id=agreement_id,
                    sku_code=product.sku_code,
                    sku_description=product.sku_description,
                    supplier_ruc=product.supplier_ruc,
                    supplier_name=product.supplier_name,
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
                    active=product.active,
                    created_at=None,  # Will be assigned by database
                    created_by_user_email=product.created_by_user_email,
                    updated_at=None,  # Will be assigned by database
                    updated_status_by_user_email=product.updated_status_by_user_email
                )
                created_products.append(created_product)
            
            logger.info(f"Bulk created {len(created_products)} products for agreement {agreement_id}")
            return created_products
            
        except Exception as e:
            logger.error(f"Failed to bulk create products for agreement {agreement_id}: {e}")
            raise

    async def _create_agreement_store_rules_bulk(self, agreement_id: int, store_rules: List[AgreementStoreRule]) -> List[AgreementStoreRule]:
        """Create multiple agreement store rules using bulk insert."""
        try:
            if not store_rules:
                return []
            
            # Prepare data for bulk insert
            store_rules_data = []
            for store_rule in store_rules:
                store_rules_data.append({
                    'agreement_id': agreement_id,
                    'store_id': store_rule.store_id,
                    'status': store_rule.status,  # Cambiado de status_id a status
                    'active': store_rule.active,
                    'created_by_user_email': store_rule.created_by_user_email,
                    'updated_status_by_user_email': store_rule.updated_status_by_user_email
                })
            
            # Execute bulk insert
            stmt = AgreementStoreRuleModel.__table__.insert().values(store_rules_data)
            await self._session.execute(stmt)
            
            # Instead of querying back, return domain entities with estimated data
            # This saves a SELECT query and improves performance significantly
            created_store_rules = []
            for store_rule in store_rules:
                created_store_rule = AgreementStoreRule(
                    id=None,  # Will be assigned by database
                    agreement_id=agreement_id,
                    store_id=store_rule.store_id,
                    status=store_rule.status,
                    active=store_rule.active,
                    created_at=None,  # Will be assigned by database
                    created_by_user_email=store_rule.created_by_user_email,
                    updated_at=None,  # Will be assigned by database
                    updated_status_by_user_email=store_rule.updated_status_by_user_email
                )
                created_store_rules.append(created_store_rule)
            
            logger.info(f"Bulk created {len(created_store_rules)} store rules for agreement {agreement_id}")
            return created_store_rules
            
        except Exception as e:
            logger.error(f"Failed to bulk create store rules for agreement {agreement_id}: {e}")
            raise

    async def _create_agreement_excluded_flags_bulk(self, agreement_id: int, excluded_flags: List[AgreementExcludedFlag]) -> List[AgreementExcludedFlag]:
        """Create multiple agreement excluded flags using bulk insert."""
        try:
            if not excluded_flags:
                return []
            
            # Prepare data for bulk insert
            excluded_flags_data = []
            for excluded_flag in excluded_flags:
                excluded_flags_data.append({
                    'agreement_id': agreement_id,
                    'excluded_flag_id': excluded_flag.excluded_flag_id,
                    'active': excluded_flag.active,
                    'created_by_user_email': excluded_flag.created_by_user_email,
                    'updated_status_by_user_email': excluded_flag.updated_status_by_user_email
                })
            
            # Execute bulk insert
            stmt = AgreementExcludedFlagModel.__table__.insert().values(excluded_flags_data)
            await self._session.execute(stmt)
            
            # Instead of querying back, return domain entities with estimated data
            # This saves a SELECT query and improves performance significantly
            created_excluded_flags = []
            for excluded_flag in excluded_flags:
                created_excluded_flag = AgreementExcludedFlag(
                    id=None,  # Will be assigned by database
                    agreement_id=agreement_id,
                    excluded_flag_id=excluded_flag.excluded_flag_id,
                    active=excluded_flag.active,
                    created_at=None,  # Will be assigned by database
                    created_by_user_email=excluded_flag.created_by_user_email,
                    updated_at=None,  # Will be assigned by database
                    updated_status_by_user_email=excluded_flag.updated_status_by_user_email
                )
                created_excluded_flags.append(created_excluded_flag)
            
            logger.info(f"Bulk created {len(created_excluded_flags)} excluded flags for agreement {agreement_id}")
            return created_excluded_flags
            
        except Exception as e:
            logger.error(f"Failed to bulk create excluded flags for agreement {agreement_id}: {e}")
            raise
    
    async def search_agreements(self, search_request: AgreementSearchRequest) -> AgreementSearchResponse:
        try:
            logger.info(f"Executing agreement search with params: {search_request.model_dump()}")

            function_call = load_sql_query("search_agreements")

            params = {
                'division_codes': format_array(search_request.division_codes),
                'status_ids': format_array(search_request.status_ids),
                'created_by_emails': format_array(search_request.created_by_emails),
                'agreement_number': search_request.agreement_number,
                'sku_code': search_request.sku_code,
                'description': search_request.description,
                'rebate_type_id': search_request.rebate_type_id,
                'concept_id': search_request.concept_id,
                'spf_code': search_request.spf_code,
                'spf_description': search_request.spf_description,
                'start_date': search_request.start_date,
                'end_date': search_request.end_date,
                'supplier_ruc': search_request.supplier_ruc,
                'supplier_name': search_request.supplier_name,
                'store_grouping_id': search_request.store_grouping_id,
                'pmm_username': search_request.pmm_username,
                'limit': search_request.limit,
                'offset': search_request.offset
            }

            # Use the injected session instead of creating a new one
            result = await self._session.execute(text(function_call), params)
            rows = result.fetchall()

            # Map results using the new comprehensive mapper
            agreement_results = map_search_results_to_agreement_items(rows)

            # Get total count from the first row if available (PostgreSQL function returns total_count)
            total_count = rows[0].total_count if rows else 0

            response = AgreementSearchResponse(
                agreements=agreement_results,
                total_count=total_count
            )

            logger.info(f"Agreement search completed successfully. Found {len(agreement_results)} filtered results out of {total_count} total matching agreements")
            return response

        except Exception as e:
            logger.error(f"Error executing agreement search: {str(e)}")
            raise