"""Store repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.interfaces.schemas.__init__ import Stores


class StoresRepository(ABC):

    @abstractmethod
    async def get_by_id(self, store_id: int) -> Optional[Stores]:
        pass

    @abstractmethod
    async def get_active_stores(self) -> List[Stores]:
        """Get all active stores ordered by store_id."""
        pass





