"""Module schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


"""Module schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


#region Base Schemas

class ModuleBase(BaseModel):
    """Base schema for Module with common fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    business_unit_id: int = Field(..., description="Business unit ID")
    name: str = Field(..., max_length=50, description="Module name")
    description: Optional[str] = Field(None, max_length=250, description="Module description")
    is_active: bool = Field(True, description="Whether the module is active")


class ModuleUserBase(BaseModel):
    """Base schema for Module User with common fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user_email: str = Field(..., max_length=320, description="User email")
    module_id: int = Field(..., description="Module ID")


class ModuleSchema(ModuleBase):
    """Schema for Module entity with all fields."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModuleUserSchema(ModuleUserBase):
    """Schema for Module User entity with all fields."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

#endregion


#region Request Schemas

class ModuleIdRequest(BaseModel):
    """Schema for module ID request validation."""
    
    module_id: int = Field(..., gt=0, description="Module ID must be greater than 0")

#endregion


#region Response Schemas

class ActiveModuleUsersResponse(BaseModel):
    """Schema for active module users response."""
    
    user_emails: List[str]
    total_users: int


class ModulesResponse(BaseModel):
    """Schema for modules list response."""
    
    modules: List[ModuleSchema]
    total_modules: int


class ModuleUsersResponse(BaseModel):
    """Schema for module users list response."""
    
    users: List[ModuleUserSchema]
    total_users: int
    module_id: int

#endregion
