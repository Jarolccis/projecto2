from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional, List

from app.interfaces.schemas import (
    AgreementResponse,
    AgreementSearchRequest,
    AgreementSearchResponse,
    # New create agreement schemas
    AgreementCreateRequest,
    AgreementCreateResponse,
    AgreementCreateSuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
    create_error_response,
    create_paginated_response,
    create_success_response,
)

from app.interfaces.schemas.agreement_schema import AgreementDetailResponse, AgreementUpdateRequest
from app.interfaces.schemas.security_schema import Roles, User
from app.core.logging import LoggerMixin
from app.interfaces.dependencies import AgreementUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple 
router = APIRouter(
    prefix="/v1/agreements",
    tags=["agreements"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)
 
class AgreementController(LoggerMixin):
    
    async def create_agreement(
        self, 
        request: Request,
        agreement_data: AgreementCreateRequest, 
        use_cases: AgreementUseCasesDep
    ) -> AgreementCreateResponse:
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.CREATE_AGREEMENTS])

            self.log_info(
                "Iniciando creación de acuerdo", 
                business_unit_id=user.bu_id,
                agreement_type_id=agreement_data.agreement_type_id,
                source_system=agreement_data.source_system.value,
                products_count=len(agreement_data.products),
                store_rules_count=len(agreement_data.store_rules),
                excluded_flags_count=len(agreement_data.excluded_flags)
            )
            
            agreement = await use_cases.create_agreement(agreement_data, user)
            
            response_data = AgreementCreateResponse.from_domain_model(agreement)
            
            self.log_info(
                "Acuerdo creado exitosamente", 
                agreement_id=agreement.id,
                business_unit_id=agreement.business_unit_id
            )
            
            return response_data
            
        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning(
                "Error de validación al crear acuerdo", 
                error_message=str(e),
                business_unit_id=agreement_data.business_unit_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error inesperado al crear acuerdo", 
                error=e,
                business_unit_id=agreement_data.business_unit_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

    async def search_agreements(
        self,
        request: Request,
        search_request: AgreementSearchRequest,
        use_cases: AgreementUseCasesDep
    ) -> PaginatedResponse[AgreementSearchResponse]:
        """Search agreements with advanced filters."""
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info(
                "Iniciando búsqueda de acuerdos",
                limit=search_request.limit,
                offset=search_request.offset,
                has_filters=bool(
                    search_request.division_codes or 
                    search_request.status_ids or 
                    search_request.created_by_emails or 
                    search_request.agreement_number or
                    search_request.sku_code or
                    search_request.spf_code or
                    search_request.supplier_ruc or
                    search_request.supplier_name
                )
            )

            search_result = await use_cases.search_agreements(search_request)
            
            skip = search_request.offset or 0
            limit = search_request.limit or 100
            total = search_result.total_count
            returned_count = len(search_result.agreements)
            
            pagination = {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_next": (skip + returned_count) < total,
                "has_prev": skip > 0
            }
            
            self.log_info(
                "Búsqueda de acuerdos completada exitosamente",
                total_found=total,
                returned_count=returned_count,
                skip=skip,
                limit=limit
            )
            
            return create_paginated_response(
                data=search_result,
                pagination=pagination,
                message=f"Retrieved {returned_count} agreements out of {total} total"
            )
            
        except HTTPException:
            raise
        except ValueError as e:
            self.log_error(
                "Error de validación en búsqueda de acuerdos", 
                error=e
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message=f"Invalid search parameters: {str(e)}"
                ).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error al buscar acuerdos", 
                error=e
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

    async def get_agreement_by_id(
        self,
        request: Request,
        agreement_id: int,
        use_cases: AgreementUseCasesDep
    ) -> SuccessResponse[AgreementDetailResponse]:
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info(
                "Iniciando obtención de detalle de acuerdo",
                agreement_id=agreement_id,
                user_email=user.email,
                business_unit_id=user.bu_id
            )

            agreement_detail = await use_cases.get_agreement_by_id(agreement_id)

            self.log_info(
                "Detalle de acuerdo obtenido exitosamente",
                agreement_id=agreement_id,
                products_count=len(agreement_detail.products),
                store_rules_count=len(agreement_detail.store_rules),
                excluded_flags_count=len(agreement_detail.excluded_flags)
            )

            return create_success_response(
                data=agreement_detail,
                message="Agreement details retrieved successfully"
            )

        except ValueError as e:
            self.log_error(
                "Error de validación al obtener detalle de acuerdo",
                error=e,
                agreement_id=agreement_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message=str(e)
                ).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error al obtener detalle de acuerdo",
                error=e,
                agreement_id=agreement_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

    async def update_agreement(
        self,
        request: Request,
        agreement_id: int,
        agreement_data: AgreementUpdateRequest,
        use_cases: AgreementUseCasesDep
    ) -> AgreementResponse:
        """Update an existing agreement."""
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.MODIFY_AGREEMENTS])

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
            
            agreement = await use_cases.update_agreement(agreement_id, agreement_data, user)
            
            self.log_info(
                "Acuerdo actualizado exitosamente", 
                agreement_id=agreement.id,
                business_unit_id=agreement.business_unit_id
            )
            
            return agreement
            
        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning(
                "Error de validación al actualizar acuerdo", 
                error_message=str(e),
                agreement_id=agreement_id,
                business_unit_id=agreement_data.business_unit_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error inesperado al actualizar acuerdo", 
                error=e,
                agreement_id=agreement_id,
                business_unit_id=agreement_data.business_unit_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

controller = AgreementController()

@router.post(
    "/",
    response_model=AgreementCreateSuccessResponse,
    summary="Create a new agreement",
    description="Create a new agreement with all related products, store rules, and excluded flags"
)
async def create_agreement(
    request: Request,
    agreement_data: AgreementCreateRequest,
    use_cases: AgreementUseCasesDep,
) -> AgreementCreateSuccessResponse:
    response_data = await controller.create_agreement(request, agreement_data, use_cases)
    return create_success_response(
        data=response_data,
        message="Agreement created successfully"
    )



@router.post(
    "/search",
    response_model=PaginatedResponse[AgreementSearchResponse],
    summary="Search agreements with advanced filters",
    description="Search agreements using multiple filters including business units, agreement types, suppliers, dates, and more. Supports pagination."
)
async def search_agreements(
    request: Request,
    search_request: AgreementSearchRequest,
    use_cases: AgreementUseCasesDep
) -> PaginatedResponse[AgreementSearchResponse]:
    return await controller.search_agreements(request, search_request, use_cases)

@router.get(
    "/{agreement_id}",
    response_model=SuccessResponse[AgreementDetailResponse],
    summary="Get agreement details by ID",
    description="Retrieve agreement details including all related products, store rules, and excluded flags"
)
async def get_agreement_by_id(
    request: Request,
    agreement_id: int,
    use_cases: AgreementUseCasesDep
) -> SuccessResponse[AgreementDetailResponse]:
    return await controller.get_agreement_by_id(request, agreement_id, use_cases)

@router.put(
    "/{agreement_id}",
    response_model=SuccessResponse[AgreementResponse],
    summary="Update an existing agreement",
    description="Update an existing agreement with all related products, store rules, and excluded flags. This will replace all existing related data."
)
async def update_agreement(
    request: Request,
    agreement_id: int,
    agreement_data: AgreementUpdateRequest,
    use_cases: AgreementUseCasesDep
) -> SuccessResponse[AgreementResponse]:
    agreement = await controller.update_agreement(request, agreement_id, agreement_data, use_cases)
    return create_success_response(
        data=agreement,
        message="Agreement updated successfully"
    )
