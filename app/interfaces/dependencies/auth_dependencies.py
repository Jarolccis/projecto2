"""Authentication dependencies for FastAPI."""

import logging
from typing import List, Optional
from fastapi import HTTPException, Header, Depends, Request
from sqlalchemy.orm import Session
from starlette import status

from app.interfaces.schemas.security_schema import User, Roles
from app.domain.repositories.user_permissions_repository import UserPermissionsRepository
from app.domain.repositories.security_repository import SecurityContextRepository, AuthenticationStrategy
from app.core.utils import get_bu_id
from app.core.constants import (
    TOKEN_REQUIRED, USER_INACTIVE, NOT_BU, NOT_ALLOW
)

# Import infrastructure components
from app.infrastructure.postgres.session import AsyncSessionLocal
from app.infrastructure.repositories.user_permissions_repository import UserPermissionsRepository as ConcreteUserPermissionsRepository
from app.core.security_context import SecurityContext
from app.core.keycloak_strategy import KeyCloakStrategy


def get_permissions_repository() -> UserPermissionsRepository:
    """
    Get permissions repository instance.
    This is where we decide which implementation to use.
    Deprecated: Use check_db_permissions_simple instead for new code.
    """
    # Create a session - note this is for backward compatibility only
    session = AsyncSessionLocal()
    return ConcreteUserPermissionsRepository(session)


def get_security_context() -> SecurityContextRepository:
    """
    Determine strategy for authentication and authorization.
    Uses dependency injection to provide implementations.
    """
    strategy: AuthenticationStrategy = KeyCloakStrategy()
    context: SecurityContextRepository = SecurityContext(strategy)
    return context


async def security(
    country: str, 
    authorization: Optional[str] = None, 
    permissions: Optional[List[str]] = None
) -> User:
    """
    Main security function for authentication and authorization.
    
    :param permissions: list of permissions
    :param authorization: token from header
    :param country: country header
    :return: User
    """
    context = get_security_context()
    
    if not context.extract_authorization(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=TOKEN_REQUIRED
        )
        
    if not context.verify():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=context.response_valid_token.reason_reject if context.response_valid_token else "Token validation failed"
        )
        
    if not context.is_active_user():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=USER_INACTIVE
        )
        
    if not context.has_bu(bu='TOT', country=country):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=NOT_BU
        )
        
    if not context.has_permissions(permissions=permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=NOT_ALLOW
        )
    
    # Ensure we have a user before modifying properties
    if not context.user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User context not available"
        )
    
    # Get user and set additional properties
    user = context.user
    user.token = context.token
    user.bu_id = get_bu_id(country)
    user.country = country
    user.bu = 'TOT'
    
    return user


def check_token(permissions: Optional[List[str]] = None):
    """
    Dependency factory for token checking.
    """
    async def inner(
        country: str = Header(..., description="Country code"),
        authorization: str = Header(None, description="Bearer token")
    ):
        return await security(country, authorization, permissions)
    
    return inner


async def get_current_user(
    country: str = Header(..., description="Country code"),
    authorization: str = Header(None, description="Bearer token")
) -> User:
    """Get current authenticated user dependency."""
    return await security(country, authorization)


def require_permissions(permissions: List[str]):
    """
    Dependency factory for permission checking.
    """
    async def check_permissions(
        country: str = Header(..., description="Country code"),
        authorization: str = Header(None, description="Bearer token")
    ) -> User:
        return await security(country, authorization, permissions)
    
    return check_permissions


def require_permissions_internal(permissions: List[Roles]):
    """
    Dependency factory for internal permission checking (with DB validation).
    This handles DB internally without exposing it to the controller.
    """
    async def check_permissions(request: Request) -> User:
        # Get user from middleware
        if not hasattr(request.state, 'user') or not request.state.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        user = request.state.user
        
        # Check database permissions using the simple function
        await check_db_permissions_simple(user, permissions)
        
        return user
    
    return check_permissions


async def check_db_permissions_simple(user: User, permissions: List[Roles]) -> bool:
    """
    Simple function to check DB permissions.
    Handles DB session internally.
    Raises HTTPException if permissions are not met.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    # Create session for permissions check
    session = AsyncSessionLocal()
    try:
        permissions_repo = ConcreteUserPermissionsRepository(session)
        logging.info(f'Checking DB permissions for user "{user.email}" with BU ID {user.bu_id}')
        has_permission = await permissions_repo.check_db_permissions(user, permissions)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissions required: {[perm.value for perm in permissions]}"
            )
        
        return True
    except HTTPException:
        # Re-raise HTTPExceptions as is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking permissions: {str(e)}"
        )
    finally:
        await session.close()


async def check_db_permissions(
    user: User,
    permissions: List[Roles],
    db: Session
) -> bool:
    """
    Check permissions against database.
    Deprecated: Use check_db_permissions_simple instead.
    Remove when all code is migrated to the new pattern.
    
    Args:
        user: User from request.state.user (set by middleware)
        permissions: List of required permissions
        db: Database session (deprecated parameter)
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    permissions_repo = get_permissions_repository()
    return await permissions_repo.check_db_permissions(user, permissions)
