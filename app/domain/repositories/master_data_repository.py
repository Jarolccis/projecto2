"""Master data repository interface."""

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.division import Division


class MasterDataRepository(ABC):
    """Abstract repository for master data."""
    
    @abstractmethod
    async def get_all_divisions(self) -> List[Division]:
        """Get all divisions."""
        pass
