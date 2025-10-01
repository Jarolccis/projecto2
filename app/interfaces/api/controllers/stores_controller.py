"""Store API controller."""
from typing import List,Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
from app.interfaces.schemas import (
    ErrorResponse,
    StoreResponse,
    SuccessResponse,
    create_error_response,
    create_success_response,
) 
from app.core.logging import LoggerMixin
from app.interfaces.dependencies import StoreUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
from app.interfaces.schemas.security_schema import Roles, User 

router = APIRouter(
    prefix="/v1/stores",
    tags=["stores"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

class StoresController(LoggerMixin):
    """Controller for store operations with logging capabilities."""
    
    async def get_active_stores(        
        self,
        request: Request,
        use_cases: StoreUseCasesDep
    ) -> SuccessResponse[List[Any]]:
        """Get all active stores ordered by store_id."""
        try:

            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            self.log_info("Obteniendo tiendas activas")
            
            stores = await use_cases.get_active_stores()
             
            return create_success_response(
                data=stores,
                message=f"Retrieved {len(stores)} active stores successfully"
            )
        except Exception as e:
            self.log_error(
                "StoresController :  Error al obtener tiendas activas", 
                error=e
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

    async def get_store_by_id(
        self, 
        request: Request,
        store_id: int, 
        use_cases: StoreUseCasesDep
    ) -> SuccessResponse[StoreResponse]:
        """Get a store by ID."""
        try:

            # Obtener user del middleware
            # user: User = request.state.user

            # Validar permisos específicos de BD
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])
 
            if store_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid store ID")


            self.log_info("Buscando tienda por ID", store_id=store_id)
            
            store = await use_cases.get_store_by_id(store_id)
            if store is None:
                self.log_warning(
                    "Tienda no encontrada", 
                    store_id=store_id
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(
                        message=f"Store with ID {store_id} not found"
                    ).model_dump(),
                )
            
            self.log_info("Tienda encontrada exitosamente", store_id=store_id)
            return create_success_response(
                data=store,
                message="Store retrieved successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            self.log_error(
                "Error al obtener tienda por ID", 
                error=e,
                store_id=store_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Internal server error").model_dump(),
            )

# Instancia del controlador
store_controller = StoresController()


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get(
    "/active",
    response_model=SuccessResponse[List[Any]],
    summary="Get active stores",
    description="Retrieve all active stores ordered by store_id.",
)
async def get_active_stores(
    request: Request,
    use_cases: StoreUseCasesDep,
) -> SuccessResponse[List[Any]]:
    """Get all active stores ordered by store_id."""
    return await store_controller.get_active_stores(request, use_cases)


@router.get(
    "/{store_id}",
    response_model=SuccessResponse[StoreResponse],
    summary="Get store by ID",
    description="Retrieve a specific store by their ID.",
)
async def get_store_by_id(
    request: Request,
    store_id: int,
    use_cases: StoreUseCasesDep,
) -> SuccessResponse[StoreResponse]:
    """Get a store by ID."""
    return await store_controller.get_store_by_id(request, store_id, use_cases)

