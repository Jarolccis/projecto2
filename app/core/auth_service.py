"""Authentication domain service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.interfaces.schemas.security_schema import User, ResponseValidToken


class AuthenticationService(ABC):
    """Abstract authentication service."""
    
    @abstractmethod
    async def validate_token(self, token: str) -> ResponseValidToken:
        """Validate JWT token."""
        pass
    
    @abstractmethod
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Extract user from token."""
        pass

    @abstractmethod
    async def has_business_unit_access(self, user: User, bu: str, country: str, vendor_tax: str = None) -> bool:
        """Check if user has access to business unit."""
        pass    
    
    @abstractmethod
    async def has_permissions(self, user: User, permissions: List[str]) -> bool:
        """Check user permissions."""
        pass
    
    @abstractmethod
    async def is_active_user(self, user: User) -> bool:
        """Check if user is active."""
        pass
