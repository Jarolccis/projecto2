"""Master data API controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.interfaces.schemas.division_schema import DivisionResponse
from app.core.response import (
    SuccessResponse,
    create_error_response,
    create_success_response,
)
from app.interfaces.schemas.security_schema import Roles, User
from app.core.logging import LoggerMixin
from app.interfaces.dependencies import MasterDataUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
#router = APIRouter(prefix="/v1/master-data", tags=["master-data"])
router = APIRouter(
    prefix="/v1/master-data",
    tags=["master-data"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

class MasterDataController(LoggerMixin):
    """Controller for master data operations with logging capabilities."""
    
    async def get_all_divisions(        
        self,
        request: Request,
        use_cases: MasterDataUseCasesDep
    ) -> SuccessResponse[List[DivisionResponse]]:
        """Get all divisions."""
        try:

            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info("Obteniendo todas las divisiones")
            
            divisions = await use_cases.get_all_divisions()
            
            self.log_info(
                "Divisiones obtenidas exitosamente", 
                total_divisions=len(divisions)
            )
            
            return create_success_response(
                data=divisions,
                message=f"Retrieved {len(divisions)} divisions successfully"
            )
        except Exception as e:
            self.log_error(
                "Error al obtener divisiones", 
                error=e
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )


# Instancia del controlador
master_data_controller = MasterDataController()


@router.get(
    "/divisions",
    response_model=SuccessResponse[List[DivisionResponse]],
    summary="Get all divisions",
    description="Retrieve all divisions from BigQuery ordered by division code.",
)
async def get_all_divisions(
    request: Request,
    use_cases: MasterDataUseCasesDep,
) -> SuccessResponse[List[DivisionResponse]]:
    """Get all divisions."""
    return await master_data_controller.get_all_divisions(request, use_cases)
