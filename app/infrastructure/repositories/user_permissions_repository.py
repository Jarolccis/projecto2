"""SQLAlchemy implementation of UserPermissionsRepository."""

from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from app.interfaces.schemas.security_schema import Roles, User
from app.domain.repositories.user_permissions_repository import (
    UserPermissionsRepository,
)
from app.infrastructure.postgres.models.tottus import ModulesModel, ModuleUsersModel
from app.infrastructure.postgres.session import AsyncSessionLocal 
from app.core.constants import NOT_ALLOW

class UserPermissionsRepository(UserPermissionsRepository):
    """SQLAlchemy implementation of user permissions repository."""

    def __init__(self, session: AsyncSession = None):
        self._session = session

    async def get_permissions_by_user(
        self, 
        permissions: List[Roles], 
        user_email: str, 
        user_bu_id: int
    ) -> List[str]:
        """
        Get user permissions from database.
        Deprecated: Remove when roles are implemented in Keycloak and not in the database.
        """
        permission_names = [p.value for p in permissions]
        
        # Use async SQLAlchemy query
        stmt = (
            select(ModulesModel.name)
            .join(ModuleUsersModel, ModuleUsersModel.module_id == ModulesModel.id)
            .where(ModuleUsersModel.user_email == user_email)
            .where(ModulesModel.is_active.is_(True))
            .where(ModulesModel.business_unit_id == user_bu_id)
            .where(ModulesModel.name.in_(permission_names))
        )
        
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        
        if not rows:
            return []
            
        return list(rows)

    async def check_db_permissions(
        self, 
        user: User, 
        permissions: List[Roles]
    ) -> bool:
        """
        Check if user has required permissions in database.
        Deprecated: Remove when roles are implemented in Keycloak and not in the database.
        """
        if not user.bu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User business unit ID is required"
            )
            
        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email is required"
            )
            
        modules = await self.get_permissions_by_user(
            permissions, user.email, user.bu_id
        )
        
        missing_permissions: List[str] = []
        for permission in permissions:
            if permission.value not in modules:
                missing_permissions.append(permission.name)
                
        if missing_permissions:
            # logging.info(f'User "{user.email}" has not permissions: {missing_permissions}')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=NOT_ALLOW
            )
            
        return True
