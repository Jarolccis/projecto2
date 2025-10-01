"""Store use cases implementing business logic."""

from typing import Any, List, Optional

from app.interfaces.schemas import StoreResponse
from app.domain.repositories import StoresRepository
from app.core.logging import LoggerMixin
import time


class StoresUseCases(LoggerMixin):

    def __init__(self, store_repository: StoresRepository):
        self._store_repository = store_repository
        self.log_info(
            "StoreUseCases inicializado", 
            repository_type=type(store_repository).__name__
        )

    async def get_store_by_id(self, store_id: int) -> Optional[StoreResponse]:
        """Get a store by ID."""
        try:
            self.log_info("Buscando tienda por ID", store_id=store_id)
            store = await self._store_repository.get_by_id(store_id)
            if store is None:
                self.log_warning("Tienda no encontrada por ID", store_id=store_id)
                return None
            self.log_info("Tienda encontrada por ID", store_id=store_id)
            return StoreResponse.model_validate(store)
            
        except Exception as e:
            self.log_error(
                "Error al obtener tienda por ID", 
                error=e,
                store_id=store_id,
                repository_type=type(self._store_repository).__name__
            )
            raise

    async def get_active_stores(self) -> List[Any]:
        """Get all active stores as raw dicts."""
        try: 
            stores = await self._store_repository.get_active_stores()
            self.log_info("StoresUseCases : Tiendas activas obtenidas exitosamente", total_stores=len(stores))
            return [store.__dict__ for store in stores]
        except Exception as e:
            self.log_error("Error al obtener tiendas activas", error=e)
            raise



