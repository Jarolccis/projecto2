from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.sku import Sku


class SkuRepository(ABC):

    @abstractmethod
    async def get_skus_by_codes(self, sku_codes: List[str]) -> List[Sku]:
        pass
