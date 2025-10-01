"""PostgreSQL store repository implementation."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.schemas.__init__ import Stores
from app.domain.repositories import StoresRepository
from app.core.logging import LoggerMixin
from app.infrastructure.postgres.models.tottus.stores_model import StoresModel 


def _to_entity(model: StoresModel) -> Stores:
    """Convert StoreORM to Store entity."""
    return Stores(
        id=model.id,
        business_unit_id=model.business_unit_id,
        store_id=model.store_id,
        name=model.name,
        zone_id=model.zone_id,
        zone_name=model.zone_name,
        channel_id=model.channel_id,
        channel_name=model.channel_name,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class StoresRepository(StoresRepository, LoggerMixin):
    """PostgreSQL implementation of StoreRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, store_id: int) -> Optional[Stores]:
        try:
            model = await self._session.get(StoresModel, store_id)
            if model is None:
                self.log_info("Store not found by ID", store_id=store_id)
                return None
            
            self.log_info("Store retrieved by ID", store_id=store_id)
            return _to_entity(model)
                
        except SQLAlchemyError as e:
            self.log_error("Failed to get store by ID", error=e, store_id=store_id,repository_type=type(self).__name__)
            raise SQLAlchemyError(f"Database error while retrieving store: {str(e)}")

    async def get_active_stores(self) -> List[Stores]:
        """Get all active stores ordered by store_id."""
        try:
            stmt = (
                select(StoresModel)
                .where(StoresModel.is_active == True)
                .order_by(StoresModel.store_id)
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            self.log_info(
                "Active stores retrieved successfully",
                count=len(models)
            )
            
            return [_to_entity(m) for m in models]
                
        except SQLAlchemyError as e:
            self.log_error(
                "StoresRepository: Failed to get active stores",
                error=e,
                repository_type=type(self).__name__

            )
            raise SQLAlchemyError(f"Database error while retrieving active stores: {str(e)}")

