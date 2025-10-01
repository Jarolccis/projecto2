"""Lookup use cases."""

from typing import List, Optional

from app.interfaces.schemas.lookup_schema import (
    LookupCategoryCodeSchema,
    LookupOptionValueSchema,
)
from app.domain.entities.lookup import LookupValueResult
from app.domain.repositories.lookup_repository import LookupRepository
from app.core.logging import LoggerMixin


class LookupUseCases(LoggerMixin):

    def __init__(self, lookup_repository: LookupRepository):
        self.lookup_repository = lookup_repository

    async def get_lookup_values_by_category(self, lookup_request: LookupCategoryCodeSchema) -> List[LookupValueResult]:
        try:
            self.log_info("Getting lookup values by category", category_code=lookup_request.category_code)
            
            values = await self.lookup_repository.get_values_by_category_code(lookup_request.category_code)
            
            self.log_info(
                "Lookup values retrieved successfully",
                category_code=lookup_request.category_code,
                count=len(values)
            )
            
            return values
            
        except Exception as e:
            self.log_error(
                "Failed to get lookup values by category",
                error=e,
                category_code=lookup_request.category_code
            )
            raise

    async def get_specific_lookup_value(self, lookup_request: LookupOptionValueSchema) -> Optional[LookupValueResult]:
        try:
            self.log_info(
                "Getting specific lookup value",
                category_code=lookup_request.category_code,
                option_value=lookup_request.option_value
            )
            
            value = await self.lookup_repository.get_value_by_category_and_option(
                lookup_request.category_code, 
                lookup_request.option_value
            )
            
            if value:
                self.log_info(
                    "Lookup value found",
                    category_code=lookup_request.category_code,
                    option_value=lookup_request.option_value,
                    lookup_value_id=value.lookup_value_id
                )
            else:
                self.log_info(
                    "Lookup value not found",
                    category_code=lookup_request.category_code,
                    option_value=lookup_request.option_value
                )
            
            return value
            
        except Exception as e:
            self.log_error(
                "Failed to get specific lookup value",
                error=e,
                category_code=lookup_request.category_code,
                option_value=lookup_request.option_value
            )
            raise
