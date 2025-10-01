"""Module controllers for the API interface."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from dataclasses import asdict

from app.interfaces.schemas.module_schema import (
    ActiveModuleUsersResponse,
    ModuleIdRequest,
    ModulesResponse,
    ModuleUsersResponse,
)
from app.core.response import (
    SuccessResponse,
    create_error_response,
    create_success_response,
)
from app.interfaces.schemas.security_schema import Roles, User
from app.interfaces.dependencies import ModuleUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
from app.core.logging import LoggerMixin
#router = APIRouter(prefix="/v1/modules", tags=["modules"])
router = APIRouter(
    prefix="/v1/modules",
    tags=["modules"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

class ModulesController(LoggerMixin):
    """Controller for module operations."""

    async def get_active_module_users(
        self,
        request: Request,
        module_use_cases: ModuleUseCasesDep
    ) -> SuccessResponse[ActiveModuleUsersResponse]:
        """
        Get distinct user emails from active modules.
        """
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_AGREEMENTS])

            users_data = await module_use_cases.get_active_module_users()

            return create_success_response(
                data=users_data,
                message="Active module users retrieved successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Failed to retrieve active module users").model_dump(),
            )

    async def get_active_modules(
        self,
        request: Request,
        module_use_cases: ModuleUseCasesDep
    ) -> SuccessResponse[ModulesResponse]:
        """
        Get all active modules.
        """
        try:
            # Get user from middleware
            # user: User = request.state.user  # noqa: F841

            # Validate specific DB permissions (if applicable)
            # await check_db_permissions_simple(user, [Roles.ACCESS_MODULES])

            modules_data = await module_use_cases.get_active_modules()

            return create_success_response(
                data=modules_data,
                message="Active modules retrieved successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Failed to retrieve active modules").model_dump(),
            )

    async def get_module_users_by_module_id(
        self,
        request: Request,
        module_id: int,
        module_use_cases: ModuleUseCasesDep
    ) -> SuccessResponse[ModuleUsersResponse]:
        """
        Get all users for a specific module.
        """
        try:
            # Get user from middleware
            # user: User = request.state.user  # noqa: F841

            # Validate specific DB permissions (if applicable)
            # await check_db_permissions_simple(user, [Roles.ACCESS_MODULES])

            # Validate input using Pydantic schema
            validated_request = ModuleIdRequest(module_id=module_id)

            users_data = await module_use_cases.get_module_users_by_module_id(validated_request)

            return create_success_response(
                data=users_data,
                message=f"Users for module {module_id} retrieved successfully"
            )

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": f"Invalid module ID: {str(e)}",
                    "data": None
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Failed to retrieve module users").model_dump(),
            )

# Controller instance (global)
module_controller = ModulesController()

# Endpoints that call the class
@router.get(
    "/users/active",
    response_model=SuccessResponse[ActiveModuleUsersResponse],
    summary="Get active module users",
    description="Retrieve distinct user emails from all active modules"
)
async def get_active_module_users(
    request: Request,
    module_use_cases: ModuleUseCasesDep
) -> SuccessResponse[ActiveModuleUsersResponse]:
    """Get distinct user emails from active modules."""
    return await module_controller.get_active_module_users(
        request=request,
        module_use_cases=module_use_cases
    )


@router.get(
    "/active",
    response_model=SuccessResponse[ModulesResponse],
    summary="Get active modules",
    description="Retrieve all active modules from the system"
)
async def get_active_modules(
    request: Request,
    module_use_cases: ModuleUseCasesDep
) -> SuccessResponse[ModulesResponse]:
    """Get active modules."""
    return await module_controller.get_active_modules(
        request=request,
        module_use_cases=module_use_cases
    )




@router.get(
    "/{module_id}/users",
    response_model=SuccessResponse[ModuleUsersResponse],
    summary="Get module users",
    description="Retrieve all users for a specific module"
)
async def get_module_users_by_module_id(
    request: Request,
    module_id: int,
    module_use_cases: ModuleUseCasesDep
) -> SuccessResponse[ModuleUsersResponse]:
    """Get all users for a specific module."""
    return await module_controller.get_module_users_by_module_id(
        request=request,
        module_id=module_id,
        module_use_cases=module_use_cases
    )
