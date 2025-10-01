"""Security domain entities and enums."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Roles(str, Enum):
    """User roles enumeration."""
    
    ACCESS_BULK_UPLOAD_AGREEMENTS = 'ACCESS_BULK_UPLOAD_AGREEMENTS'
    BULK_UPLOAD_AGREEMENTS = 'BULK_UPLOAD_AGREEMENTS'
    ACCESS_AGREEMENTS = 'ACCESS_AGREEMENTS'
    CREATE_AGREEMENTS = 'CREATE_AGREEMENTS'
    MODIFY_AGREEMENTS = 'MODIFY_AGREEMENTS'
    DELETE_AGREEMENTS = 'DELETE_AGREEMENTS'
    ACCESS_PROCESSES = 'ACCESS_PROCESSES'
    ACCESS_SELLOUT = 'ACCESS_SELLOUT'


class VendorTaxOperation(BaseModel):
    """Vendor tax operation model."""
    
    businessUnit: str
    country: list[str]


class VendorTax(BaseModel):
    """Vendor tax information model."""
    
    taxId: str
    country: str
    operation: list[VendorTaxOperation]


class User(BaseModel):
    """User domain entity for authentication."""
    
    name: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    sub: Optional[str] = Field(None)
    iss: Optional[str] = Field(None)
    azp: Optional[str] = Field(None)
    resource_access: Optional[dict[str, Any]] = Field(None)
    given_name: Optional[str] = Field(None)
    family_name: Optional[str] = Field(None)
    vendors_taxs: Optional[list[VendorTax]] = Field(None, alias="vendors-taxs")
    token: Optional[str] = Field(None)
    bu_id: Optional[int] = Field(None)
    country: Optional[str] = Field(None)
    bu: Optional[str] = Field(None)

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class TokenData(BaseModel):
    """Token data extracted from JWT."""
    
    name: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    sub: Optional[str] = Field(None)
    iss: Optional[str] = Field(None)
    azp: Optional[str] = Field(None)
    resource_access: Optional[dict[str, Any]] = Field(None)
    given_name: Optional[str] = Field(None)
    family_name: Optional[str] = Field(None)
    vendors_taxs: Optional[list[VendorTax]] = Field(None, alias="vendors-taxs")
    token: Optional[str] = Field(None)
    bu_id: Optional[int] = Field(None)
    country: Optional[str] = Field(None)
    bu: Optional[str] = Field(None)

    class Config:
        populate_by_name = True
        allow_population_by_alias = True


class ResponseValidToken(BaseModel):
    """Response model for token validation."""
    
    is_valid: bool
    token_data: Optional[TokenData] = None
    reason_reject: str = ""
