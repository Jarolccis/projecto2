"""Security context for managing authentication state."""

from typing import Optional

from app.interfaces.schemas.security_schema import User, ResponseValidToken
from app.domain.repositories.security_repository import AuthenticationStrategy, SecurityContextRepository


class SecurityContext(SecurityContextRepository):
    """Context class for managing authentication strategies."""
    
    def __init__(self, strategy: AuthenticationStrategy) -> None:
        self._strategy = strategy
        self._token: Optional[str] = None
        self._user: Optional[User] = None
        self._response_valid_token: Optional[ResponseValidToken] = None

    @property
    def strategy(self) -> AuthenticationStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: AuthenticationStrategy) -> None:
        self._strategy = strategy

    @property
    def token(self) -> Optional[str]:
        """Get current token."""
        return self._token

    @property
    def user(self) -> Optional[User]:
        """Get current user."""
        return self._user

    @property
    def response_valid_token(self) -> Optional[ResponseValidToken]:
        """Get token validation response."""
        return self._response_valid_token

    def verify(self) -> bool:
        """Verify token and set user if valid."""
        if not self._token:
            return False
            
        self._response_valid_token = self._strategy.valid_token(self._token)
        if self._response_valid_token.is_valid:
            self._user = self.get_user()
        return self._response_valid_token.is_valid

    def has_bu(self, bu: str, country: str, vendor_tax: Optional[str] = None) -> bool:
        """
        Check if a business unit (bu) and a country exist in the vendors list,
        optionally filtering by vendor_tax.
        """
        if not self._user:
            return False
        return self._strategy.has_bu(bu, country, vendor_tax, self._user)

    def has_permissions(self, permissions: Optional[list[str]] = None) -> bool:
        """
        Check if user has required permissions.
        Before getting alarmed: exist endpoint without permissions configured,
        so, as user is already authenticated (previous step)
        they skip authorization review.
        """
        if not permissions:
            return True  # No permissions required
            
        if not self._user:
            return False
            
        return self._strategy.has_permissions(permissions, self._user)

    def extract_authorization(self, authorization: Optional[str]) -> bool:
        """
        Extract access_token JWT from authorization bearer.
        """
        if not authorization:
            return False
            
        parts = authorization.split(' ')
        
        if len(parts) != 2:
            return False
            
        if parts[0] != 'Bearer':
            return False
            
        self._token = parts[1]
        return True

    def is_active_user(self) -> bool:
        """Check if user is active."""
        return self._strategy.is_active()

    def get_user(self) -> User:
        """Get user from response valid token."""
        if not self._response_valid_token:
            raise ValueError("No valid token response available")
        return self._strategy.get_user(self._response_valid_token)
