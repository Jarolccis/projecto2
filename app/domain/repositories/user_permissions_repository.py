"""User permissions repository interface."""

from abc import ABC, abstractmethod
from typing import List

from app.interfaces.schemas.security_schema import User, Roles


class UserPermissionsRepository(ABC):
    """Abstract repository for user permissions."""
    
    @abstractmethod
    async def get_permissions_by_user(
        self, 
        permissions: List[Roles], 
        user_email: str, 
        user_bu_id: int
    ) -> List[str]:
        """Get user permissions from database."""
        pass
    
    @abstractmethod
    async def check_db_permissions(
        self, 
        user: User, 
        permissions: List[Roles]
    ) -> bool:
        """Check if user has required permissions in database."""
        pass
