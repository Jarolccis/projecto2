from app.interfaces.schemas import (
    AgreementResponse,
    AgreementProductResponse,
    AgreementStoreRuleResponse,
    AgreementExcludedFlagResponse,
    AgreementSearchRequest,
    AgreementSearchResponse,
    AgreementCreateRequest
)
from app.interfaces.schemas.agreement_schema import AgreementDetailResponse, AgreementUpdateRequest
from app.interfaces.schemas.__init__ import Agreement, AgreementProduct, AgreementStoreRule, AgreementExcludedFlag
from app.core.agreement_enums import StoreRuleStatusEnum
from app.domain.repositories import AgreementRepository
from app.core.logging import LoggerMixin
from app.interfaces.schemas.security_schema import User
from app.infrastructure.mappers.agreement_mappers import (
    map_update_request_to_agreement,
    map_requests_to_agreement_products,
    map_requests_to_agreement_store_rules,
    map_requests_to_agreement_excluded_flags
)

class AgreementUseCases(LoggerMixin):

    def __init__(self, agreement_repository: AgreementRepository):
        self._agreement_repository = agreement_repository
        self.log_info(
            "AgreementUseCases inicializado",
            repository_type=type(agreement_repository).__name__
        )

    async def create_agreement(self, agreement_data: AgreementCreateRequest, user: User) -> AgreementResponse:
        try:
            self.log_info(
                "Iniciando creación de acuerdo", 
                business_unit_id=user.bu_id,
                agreement_type_id=agreement_data.agreement_type_id,
                source_system=agreement_data.source_system.value,
                products_count=len(agreement_data.products),
                store_rules_count=len(agreement_data.store_rules),
                excluded_flags_count=len(agreement_data.excluded_flags)
            )
            
            # await self._validate_agreement_business_rules(agreement_data)
            
            from app.infrastructure.mappers.agreement_mappers import (
                map_request_to_agreement,
                map_requests_to_agreement_products,
                map_requests_to_agreement_store_rules,
                map_requests_to_agreement_excluded_flags
            )
            
            agreement_data.business_unit_id = user.bu_id  # Ensure BU ID is from user context
            agreement = map_request_to_agreement(agreement_data)
            agreement.created_by_user_email = user.email  # Set user email
            
            products = map_requests_to_agreement_products(agreement_data.products, 0)  # Will be set by facade
            store_rules = map_requests_to_agreement_store_rules(agreement_data.store_rules, 0)  # Will be set by facade
            excluded_flags = map_requests_to_agreement_excluded_flags(agreement_data.excluded_flags, 0)  # Will be set by facade
            
            for product in products:
                product.created_by_user_email = user.email
            for store_rule in store_rules:
                store_rule.created_by_user_email = user.email
            for excluded_flag in excluded_flags:
                excluded_flag.created_by_user_email = user.email
            
            created_agreement, created_products, created_store_rules, created_excluded_flags = (
                await self._agreement_repository.create_complete_agreement(
                    agreement, products, store_rules, excluded_flags
                )
            )
            
            response = await self._build_agreement_response(
                created_agreement, created_products, created_store_rules, created_excluded_flags
            )
            
            self.log_info(
                "Acuerdo creado exitosamente", 
                agreement_id=created_agreement.id,
                business_unit_id=created_agreement.business_unit_id,
                products_count=len(created_products),
                store_rules_count=len(created_store_rules),
                excluded_flags_count=len(created_excluded_flags)
            )
            
            return response
            
        except ValueError as e:
            self.log_warning(
                "Error de validación al crear acuerdo", 
                error_message=str(e),
                business_unit_id=agreement_data.business_unit_id
            )
            raise
        except Exception as e:
            self.log_error(
                "Error inesperado al crear acuerdo", 
                error=e,
                business_unit_id=agreement_data.business_unit_id
            )
            raise

    async def _validate_agreement_business_rules(self, agreement_data: AgreementCreateRequest) -> None:
        """Validate business rules for agreement creation."""
        try:
            if agreement_data.agreement_number:
                exists = await self._agreement_repository.exists_agreement_by_number_and_business_unit(
                    agreement_data.agreement_number,
                    agreement_data.business_unit_id
                )
                if exists:
                    raise ValueError(
                        f"Agreement number {agreement_data.agreement_number} already exists "
                        f"for business unit {agreement_data.business_unit_id}"
                    )
            
            self.log_info(
                "Validaciones de reglas de negocio exitosas",
                business_unit_id=agreement_data.business_unit_id
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.log_error(
                "Error en validación de reglas de negocio",
                error=e,
                business_unit_id=agreement_data.business_unit_id
            )
            raise ValueError("Error en validación de reglas de negocio")

    async def _build_agreement_response(
        self,
        agreement: Agreement,
        products: list[AgreementProduct],
        store_rules: list[AgreementStoreRule],
        excluded_flags: list[AgreementExcludedFlag]
    ) -> AgreementResponse:
        """Build the agreement response with all related data."""
        try:
            product_responses = [
                AgreementProductResponse(
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
                    updated_status_by_user_email=product.updated_status_by_user_email,
                    updated_at=product.updated_at.isoformat() if product.updated_at else None
                )
                for product in products
            ]
            
            store_rule_responses = [
                AgreementStoreRuleResponse(
                    id=store_rule.id,
                    agreement_id=store_rule.agreement_id,
                    store_id=store_rule.store_id,
                    status=store_rule.status.value if hasattr(store_rule.status, 'value') else str(store_rule.status),
                    active=store_rule.active,
                    created_at=store_rule.created_at.isoformat() if store_rule.created_at else None,
                    created_by_user_email=store_rule.created_by_user_email,
                    updated_status_by_user_email=store_rule.updated_status_by_user_email,
                    updated_at=store_rule.updated_at.isoformat() if store_rule.updated_at else None,
                    store_name=store_rule.store_name
                )
                for store_rule in store_rules
            ]
            
            excluded_flag_responses = [
                AgreementExcludedFlagResponse(
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
                for excluded_flag in excluded_flags
            ]
            
            response = AgreementResponse(
                id=agreement.id,
                business_unit_id=agreement.business_unit_id,
                agreement_number=agreement.agreement_number,
                start_date=agreement.start_date,
                end_date=agreement.end_date,
                agreement_type_id=agreement.agreement_type_id,
                status_id=agreement.status_id,
                status_name=None,  # Optional status name
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
                created_at=agreement.created_at.isoformat(),
                created_by_user_email=agreement.created_by_user_email,
                updated_at=agreement.updated_at.isoformat(),
                updated_status_by_user_email=agreement.updated_status_by_user_email,
                products=product_responses,
                store_rules=store_rule_responses,
                excluded_flags=excluded_flag_responses
            )
            
            return response
            
        except Exception as e:
            self.log_error(
                "Error al construir respuesta del acuerdo",
                error=e,
                agreement_id=agreement.id
            )
            raise ValueError("Error al construir respuesta del acuerdo")

    async def search_agreements(self, search_request: AgreementSearchRequest) -> AgreementSearchResponse:
        """Search agreements using advanced filters."""
        try:
            self.log_info(
                "Iniciando búsqueda de acuerdos",
                limit=search_request.limit,
                offset=search_request.offset,
                filters_count=len([f for f in [
                    search_request.division_codes,
                    search_request.status_ids,
                    search_request.created_by_emails,
                    search_request.agreement_number,
                    search_request.sku_code,
                    search_request.description,
                    search_request.rebate_type_id,
                    search_request.concept_id,
                    search_request.spf_code,
                    search_request.spf_description,
                    search_request.supplier_ruc,
                    search_request.supplier_name,
                    search_request.store_grouping_id,
                    search_request.pmm_username
                ] if f])
            )
            
            if search_request.limit and search_request.limit > 1000:
                raise ValueError("Limit cannot exceed 1000 records")
            
            if search_request.offset and search_request.offset < 0:
                raise ValueError("Offset cannot be negative")
            
            search_result = await self._agreement_repository.search_agreements(search_request)
            
            self.log_info(
                "Búsqueda de acuerdos completada exitosamente",
                total_found=search_result.total_count,
                returned_count=len(search_result.agreements)
            )
            
            return search_result
            
        except ValueError as ve:
            self.log_error(
                "Error de validación en búsqueda de acuerdos",
                error=ve,
                search_params=search_request.model_dump()
            )
            raise
        except Exception as e:
            self.log_error(
                "Error inesperado en búsqueda de acuerdos",
                error=e,
                search_params=search_request.model_dump()
            )
            raise ValueError("Error al buscar acuerdos")

    async def get_agreement_by_id(self, agreement_id: int) -> AgreementDetailResponse:
        """Get agreement by ID with all related data."""
        try:
            self.log_info(
                "Iniciando obtención de detalle de acuerdo",
                agreement_id=agreement_id
            )
            
            # Get agreement with all related data
            agreement_data = await self._agreement_repository.get_agreement_with_details(agreement_id)
            
            if agreement_data is None:
                raise ValueError(f"Agreement with ID {agreement_id} not found")
            
            agreement, products, store_rules, excluded_flags = agreement_data
            
            # Map to response schema
            from app.infrastructure.mappers.agreement_mappers import (
                map_agreement_to_response,
                map_products_to_response,
                map_store_rules_to_response,
                map_excluded_flags_to_response
            )
            
            agreement_response = map_agreement_to_response(agreement)
            products_response = map_products_to_response(products)
            store_rules_response = map_store_rules_to_response(store_rules)
            excluded_flags_response = map_excluded_flags_to_response(excluded_flags)
            
            detail_response = AgreementDetailResponse(
                **agreement_response.model_dump(exclude={"products", "store_rules", "excluded_flags"}),
                products=products_response,
                store_rules=store_rules_response,
                excluded_flags=excluded_flags_response
            )
            
            self.log_info(
                "Detalle de acuerdo obtenido exitosamente",
                agreement_id=agreement_id,
                products_count=len(products_response),
                store_rules_count=len(store_rules_response),
                excluded_flags_count=len(excluded_flags_response)
            )
            
            return detail_response
            
        except ValueError as ve:
            self.log_error(
                "Error de validación al obtener detalle de acuerdo",
                error=ve,
                agreement_id=agreement_id
            )
            raise
        except Exception as e:
            self.log_error(
                "Error inesperado al obtener detalle de acuerdo",
                error=e,
                agreement_id=agreement_id
            )
            raise ValueError(f"Error al obtener detalle del acuerdo {agreement_id}")

    async def update_agreement(self, agreement_id: int, agreement_data: AgreementUpdateRequest, user: User) -> AgreementResponse:
        """Update an existing agreement with all related data."""
        try:
            self.log_info(
                "Iniciando actualización de acuerdo", 
                agreement_id=agreement_id,
                business_unit_id=user.bu_id,
                agreement_type_id=agreement_data.agreement_type_id,
                source_system=agreement_data.source_system.value,
                products_count=len(agreement_data.products),
                store_rules_count=len(agreement_data.store_rules),
                excluded_flags_count=len(agreement_data.excluded_flags)
            )
            
            # Verify that the agreement exists
            existing_agreement = await self._agreement_repository.get_agreement_by_id(agreement_id)
            if not existing_agreement:
                raise ValueError(f"Agreement with ID {agreement_id} not found")
            
            # Validate business rules
            await self._validate_agreement_business_rules_for_update(agreement_id, agreement_data)
                        
            # Set business_unit_id from user context if not provided
            if agreement_data.business_unit_id is None:
                agreement_data.business_unit_id = user.bu_id
            
            agreement = map_update_request_to_agreement(agreement_data)
            agreement.updated_status_by_user_email = user.email  # Set updater email
            
            products = map_requests_to_agreement_products(agreement_data.products, agreement_id)
            store_rules = map_requests_to_agreement_store_rules(agreement_data.store_rules, agreement_id)
            excluded_flags = map_requests_to_agreement_excluded_flags(agreement_data.excluded_flags, agreement_id)
            
            # Set user email for all related entities
            for product in products:
                product.created_by_user_email = user.email
            for store_rule in store_rules:
                store_rule.created_by_user_email = user.email
            for excluded_flag in excluded_flags:
                excluded_flag.created_by_user_email = user.email
            
            # Update the complete agreement
            updated_agreement, updated_products, updated_store_rules, updated_excluded_flags = (
                await self._agreement_repository.update_complete_agreement(
                    agreement_id, agreement, products, store_rules, excluded_flags
                )
            )
            
            response = await self._build_agreement_response(
                updated_agreement, updated_products, updated_store_rules, updated_excluded_flags
            )
            
            self.log_info(
                "Acuerdo actualizado exitosamente", 
                agreement_id=updated_agreement.id,
                business_unit_id=updated_agreement.business_unit_id,
                products_count=len(updated_products),
                store_rules_count=len(updated_store_rules),
                excluded_flags_count=len(updated_excluded_flags)
            )
            
            return response
            
        except ValueError as e:
            self.log_warning(
                "Error de validación al actualizar acuerdo", 
                error_message=str(e),
                agreement_id=agreement_id,
                business_unit_id=user.bu_id
            )
            raise
        except Exception as e:
            self.log_error(
                "Error inesperado al actualizar acuerdo", 
                error=e,
                agreement_id=agreement_id,
                business_unit_id=user.bu_id
            )
            raise ValueError(f"Error al actualizar el acuerdo {agreement_id}")

    async def _validate_agreement_business_rules_for_update(self, agreement_id: int, agreement_data: AgreementUpdateRequest) -> None:
        """Validate business rules for agreement update."""
        try:
            # Validate products exist and are not duplicated
            product_skus = [product.sku_code for product in agreement_data.products]
            if len(product_skus) != len(set(product_skus)):
                raise ValueError("Duplicate products found in request")
            
            # # Validate store rules don't have duplicated store IDs
            # store_ids = [rule.store_id for rule in agreement_data.store_rules]
            # if len(store_ids) != len(set(store_ids)):
            #     raise ValueError("Duplicate store rules found in request")
            
            # Validate excluded flags don't have duplicated flag IDs  
            flag_ids = [flag.excluded_flag_id for flag in agreement_data.excluded_flags]
            if len(flag_ids) != len(set(flag_ids)):
                raise ValueError("Duplicate excluded flags found in request")
            
            self.log_info(
                "Business rules validation passed for agreement update",
                agreement_id=agreement_id,
                products_count=len(agreement_data.products),
                store_rules_count=len(agreement_data.store_rules),
                excluded_flags_count=len(agreement_data.excluded_flags)
            )
            
        except ValueError:
            raise
        except Exception as e:
            self.log_error(f"Error validating business rules for agreement update: {e}")
            raise ValueError("Error validating business rules")
