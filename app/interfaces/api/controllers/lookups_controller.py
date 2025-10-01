from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.interfaces.schemas.lookup_schema import (
    LookupCategoryCodeRequest,
    LookupOptionValueRequest,
    LookupValueResponse,
    LookupValuesResponse,
    LookupValueSingleResponse,
)
from app.core.response import (
    SuccessResponse,
    create_error_response,
    create_success_response,
)
from app.domain.entities.lookup import LookupValueResult
from app.interfaces.schemas.security_schema import Roles, User
from app.core.logging import LoggerMixin
from app.interfaces.dependencies import LookupUseCasesDep
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
from app.interfaces.dependencies.headers import get_country_header, security_scheme
#router = APIRouter(prefix="/v1/lookups", tags=["lookups"])
router = APIRouter(
    prefix="/v1/lookups",
    tags=["lookups"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

class LookupController(LoggerMixin):

    async def get_lookup_values_by_category(
        self,
        request: Request,
        category_code: str,
        lookup_use_cases: LookupUseCasesDep
    ) -> LookupValuesResponse:
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info("Obteniendo valores de lookup por categoría", category_code=category_code)

            validated_request = LookupCategoryCodeRequest(category_code=category_code)

            values = await lookup_use_cases.get_lookup_values_by_category(validated_request)

            response_data = LookupValuesResponse.from_domain_models(values, category_code)

            self.log_info(
                "Valores de lookup obtenidos exitosamente", 
                category_code=category_code,
                total_values=response_data.count
            )

            return response_data

        except HTTPException:
            raise
        except ValueError as e:
            self.log_error(
                "Error de validación en categoría de lookup", 
                error=e,
                category_code=category_code
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message=f"Invalid category code format: {str(e)}"
                ).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error al obtener valores de lookup por categoría", 
                error=e,
                category_code=category_code
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

    async def get_specific_lookup_value(
        self,
        request: Request,
        category_code: str,
        option_value: str,
        lookup_use_cases: LookupUseCasesDep
    ) -> LookupValueSingleResponse:
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info(
                "Buscando valor específico de lookup", 
                category_code=category_code,
                option_value=option_value
            )

            validated_request = LookupOptionValueRequest(
                category_code=category_code,
                option_value=option_value
            )

            value = await lookup_use_cases.get_specific_lookup_value(validated_request)

            if not value:
                self.log_warning(
                    "Valor de lookup no encontrado", 
                    category_code=category_code,
                    option_value=option_value
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(
                        message=f"Lookup value not found for category '{category_code}' and option '{option_value}'"
                    ).model_dump(),
                )

            response_data = LookupValueSingleResponse.from_domain_model(value, category_code, option_value)

            self.log_info(
                "Valor específico de lookup encontrado exitosamente", 
                category_code=category_code,
                option_value=option_value
            )

            return response_data

        except HTTPException:
            raise
        except ValueError as e:
            self.log_error(
                "Error de validación en valor específico de lookup", 
                error=e,
                category_code=category_code,
                option_value=option_value
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message=f"Invalid input format: {str(e)}"
                ).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error al obtener valor específico de lookup", 
                error=e,
                category_code=category_code,
                option_value=option_value
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

lookup_controller = LookupController()


@router.get(
    "/categories/{category_code}/values",
    response_model=LookupValuesResponse,
    summary="Get lookup values by category",
    description="Retrieve all active lookup values for a specific category code",
)
async def get_lookup_values_by_category(
    request: Request,
    category_code: str,
    lookup_use_cases: LookupUseCasesDep,
) -> LookupValuesResponse:
    return await lookup_controller.get_lookup_values_by_category(request, category_code, lookup_use_cases)


@router.get(
    "/categories/{category_code}/values/{option_value}",
    response_model=LookupValueSingleResponse,
    summary="Get specific lookup value",
    description="Retrieve specific lookup value by category code and option value",
)
async def get_specific_lookup_value(
    request: Request,
    category_code: str,
    option_value: str,
    lookup_use_cases: LookupUseCasesDep,
) -> LookupValueSingleResponse:
    return await lookup_controller.get_specific_lookup_value(request, category_code, option_value, lookup_use_cases)
