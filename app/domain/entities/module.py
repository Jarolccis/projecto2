"""Module domain entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Module:
    """Module domain entity."""
    
    id: Optional[int]
    business_unit_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        business_unit_id: int,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> "Module":
        """Create a new module instance."""
        now = datetime.utcnow()
        return cls(
            id=None,
            business_unit_id=business_unit_id,
            name=name,
            description=description,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        """Update module fields."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = datetime.utcnow()


@dataclass
class ModuleUser:
    """Module User domain entity."""
    
    id: Optional[int]
    user_email: str
    module_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        user_email: str,
        module_id: int,
    ) -> "ModuleUser":
        """Create a new module user instance."""
        now = datetime.utcnow()
        return cls(
            id=None,
            user_email=user_email,
            module_id=module_id,
            created_at=now,
            updated_at=now,
        )
