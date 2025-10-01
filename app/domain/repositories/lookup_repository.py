from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.lookup import LookupCategory, LookupValue, LookupValueResult


class LookupRepository(ABC):
    
    @abstractmethod
    async def get_values_by_category_code(self, code: str) -> List[LookupValueResult]:
        pass
    
    @abstractmethod
    async def get_value_by_category_and_option(self, category_code: str, option_value: str) -> Optional[LookupValueResult]:
        pass
