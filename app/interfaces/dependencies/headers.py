"""Authentication headers dependency for API documentation."""

from fastapi import Header, HTTPException
from fastapi.security import HTTPBearer
from typing import Optional


# Security scheme for Swagger UI
security_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="Enter your JWT token"
)


def get_country_header(
    country: str = Header(..., description="Country code (required)")
) -> str:
    """Get country header dependency."""
    return country


def get_auth_headers(
    country: str = Header(..., description="Country code (required)"),
    authorization: Optional[str] = Header(None, description="Bearer token for authentication")
) -> tuple[str, Optional[str]]:
    """
    Dependency to document authentication headers in Swagger.
    The middleware already validates these headers, so this is just for documentation.
    
    Args:
        country: Country code (e.g., PE, CL, CO)
        authorization: Bearer token for authentication
        
    Returns:
        Tuple of country and authorization token
    """
    return country, authorization
