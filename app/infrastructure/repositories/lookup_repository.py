from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.lookup import LookupCategory, LookupValue, LookupValueResult
from app.domain.repositories.lookup_repository import LookupRepository
from app.core.logging import LoggerMixin
from app.infrastructure.mappers import map_query_result_to_lookup_value_result
from app.infrastructure.postgres.models.tottus.lookup_category_model import (
    LookupCategoryModel,
)
from app.infrastructure.postgres.models.tottus.lookup_value_model import (
    LookupValueModel,
)


class PostgresLookupRepository(LookupRepository, LoggerMixin):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_values_by_category_code(self, code: str) -> List[LookupValueResult]:
        try:
            stmt = (
                select(
                    LookupValueModel.id.label('lookup_value_id'),
                    LookupValueModel.option_key,
                    LookupValueModel.display_value,
                    LookupValueModel.option_value,
                    LookupValueModel.extra_data.label('metadata'),
                    LookupValueModel.sort_order,
                    LookupValueModel.parent_id
                )
                .select_from(LookupCategoryModel)
                .join(
                    LookupValueModel, 
                    (LookupValueModel.category_id == LookupCategoryModel.id) & 
                    (LookupValueModel.active == True)
                )
                .where(
                    LookupCategoryModel.code == code,
                    LookupCategoryModel.active == True
                )
                .order_by(LookupValueModel.sort_order)
            )
            
            results = (await self._session.execute(stmt)).all()
            
            lookup_results = [
                map_query_result_to_lookup_value_result(row) for row in results
            ]
            
            self.log_info(
                "Lookup values retrieved by category code",
                category_code=code,
                count=len(lookup_results)
            )
            
            return lookup_results
                
        except SQLAlchemyError as e:
            self.log_error(
                "Failed to get values by category code", 
                error=e, 
                category_code=code
            )
            raise SQLAlchemyError(f"Database error while retrieving lookup values: {str(e)}")

    async def get_value_by_category_and_option(self, category_code: str, option_value: str) -> Optional[LookupValueResult]:
        try:
            stmt = (
                select(
                    LookupValueModel.id.label('lookup_value_id'),
                    LookupValueModel.option_key,
                    LookupValueModel.display_value,
                    LookupValueModel.option_value,
                    LookupValueModel.extra_data.label('metadata'),
                    LookupValueModel.sort_order,
                    LookupValueModel.parent_id
                )
                .select_from(LookupCategoryModel)
                .join(
                    LookupValueModel, 
                    (LookupValueModel.category_id == LookupCategoryModel.id) & 
                    (LookupValueModel.active == True)
                )
                .where(
                    LookupCategoryModel.code == category_code,
                    LookupValueModel.option_value == option_value,
                    LookupCategoryModel.active == True
                )
                .order_by(LookupValueModel.sort_order)
            )
            
            result = (await self._session.execute(stmt)).first()
            
            if result is None:
                self.log_info(
                    "Lookup value not found",
                    category_code=category_code,
                    option_value=option_value
                )
                return None
            
            lookup_result = map_query_result_to_lookup_value_result(result)
            
            self.log_info(
                "Lookup value retrieved by category and option",
                category_code=category_code,
                option_value=option_value,
                lookup_value_id=lookup_result.lookup_value_id
            )
            
            return lookup_result
                
        except SQLAlchemyError as e:
            self.log_error(
                "Failed to get value by category and option", 
                error=e, 
                category_code=category_code,
                option_value=option_value
            )
            raise SQLAlchemyError(f"Database error while retrieving lookup value: {str(e)}")
