from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
from app.interfaces.schemas.security_schema import Roles, User
from app.interfaces.schemas.sku_schema import SkuCodesRequest, SkusResponse
from app.core.response import create_error_response
from app.core.logging import LoggerMixin
from app.interfaces.dependencies import SkuUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
#router = APIRouter(prefix="/v1/skus", tags=["skus"])
router = APIRouter(
    prefix="/v1/skus",
    tags=["skus"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

class SkuController(LoggerMixin):

    async def get_skus_by_codes(
        self,
        request: Request,
        sku_codes: str,
        sku_use_cases: SkuUseCasesDep
    ) -> SkusResponse:
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])
            
            sku_codes_list = [code.strip() for code in sku_codes.split(',') if code.strip()]
            
            self.log_info(
                "Obteniendo SKUs por códigos",
                sku_codes_count=len(sku_codes_list),
                sku_codes=sku_codes_list[:5]  # Log solo los primeros 5
            )

            validated_request = SkuCodesRequest(sku_codes=sku_codes_list)

            skus = await sku_use_cases.get_skus_by_codes(validated_request)

            response_data = SkusResponse.from_domain_models(skus, sku_codes_list)

            self.log_info(
                "SKUs obtenidos exitosamente",
                requested_count=len(sku_codes_list),
                found_count=response_data.count
            )

            return response_data

        except ValueError as e:
            self.log_error(
                "Error de validación al obtener SKUs",
                error=e,
                sku_codes=sku_codes
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message=f"Invalid SKU codes: {str(e)}"
                ).model_dump(),
            )
        except Exception as e:
            self.log_error(
                "Error al obtener SKUs por códigos",
                error=e,
                sku_codes=sku_codes
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )


sku_controller = SkuController()


@router.get(
    "/by-codes",
    response_model=SkusResponse,
    summary="Get SKUs by codes",
    description="Retrieve SKU information by providing a list of SKU codes",
)
async def get_skus_by_codes(
    request: Request,
    sku_codes: str,
    sku_use_cases: SkuUseCasesDep,
) -> SkusResponse:
    return await sku_controller.get_skus_by_codes(request, sku_codes, sku_use_cases)
