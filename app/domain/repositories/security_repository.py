"""Security repository abstractions for authentication and authorization."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.interfaces.schemas.security_schema import User, ResponseValidToken


class AuthenticationStrategy(ABC):
    """Abstract authentication strategy interface."""
    
    @abstractmethod
    def valid_token(self, token: str) -> ResponseValidToken:
        """Validate authentication token."""
        pass

    @abstractmethod
    def get_user(self, response_valid_token: ResponseValidToken) -> User:
        """Get user from valid token response."""
        pass

    @abstractmethod
    def has_bu(self, bu: str, country: str, vendor_tax: Optional[str] = None, user: Optional[User] = None) -> bool:
        """Check business unit access."""
        pass

    @abstractmethod
    def has_permissions(self, permissions: List[str], user: User) -> bool:
        """Check user permissions."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Check if user is active."""
        pass


class SecurityContextRepository(ABC):
    """Abstract security context repository interface."""
    
    @abstractmethod
    def extract_authorization(self, authorization: Optional[str]) -> bool:
        """Extract and validate authorization header."""
        pass
    
    @abstractmethod
    def verify(self) -> bool:
        """Verify token validity."""
        pass
    
    @abstractmethod
    def is_active_user(self) -> bool:
        """Check if user is active."""
        pass
    
    @abstractmethod
    def has_bu(self, bu: str, country: str, vendor_tax: Optional[str] = None) -> bool:
        """Check business unit access."""
        pass
    
    @abstractmethod
    def has_permissions(self, permissions: Optional[List[str]] = None) -> bool:
        """Check user permissions."""
        pass
    
    @property
    @abstractmethod
    def user(self) -> Optional[User]:
        """Get current user."""
        pass
    
    @property
    @abstractmethod
    def token(self) -> Optional[str]:
        """Get current token."""
        pass
    
    @property
    @abstractmethod
    def response_valid_token(self) -> Optional[ResponseValidToken]:
        """Get token validation response."""
        pass
