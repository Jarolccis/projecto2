"""Module repository interface."""

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.module import Module, ModuleUser


class ModulesRepository(ABC):
    """Abstract base class for module repository."""

    @abstractmethod
    async def get_active_module_users(self) -> List[str]:
        """Get distinct user emails from active modules."""
        pass

    @abstractmethod
    async def get_active_modules(self) -> List[Module]:
        """Get all active modules."""
        pass

    @abstractmethod
    async def get_module_users_by_module_id(self, module_id: int) -> List[ModuleUser]:
        """Get all users for a specific module."""
        pass
