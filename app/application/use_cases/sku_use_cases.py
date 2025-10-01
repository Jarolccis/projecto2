from typing import List
from app.interfaces.schemas.sku_schema import SkuCodesRequest
from app.domain.entities.sku import Sku
from app.domain.repositories.sku_repository import SkuRepository
from app.core.logging import LoggerMixin


class SkuUseCases(LoggerMixin):

    def __init__(self, sku_repository: SkuRepository):
        self.sku_repository = sku_repository
        self.log_info(
            "SkuUseCases inicializado",
            repository_type=type(sku_repository).__name__
        )

    async def get_skus_by_codes(self, sku_request: SkuCodesRequest) -> List[Sku]:
        try:
            self.log_info(
                "Obteniendo SKUs por códigos",
                sku_codes_count=len(sku_request.sku_codes),
                sku_codes=sku_request.sku_codes[:5]
            )
            
            unique_codes = list(set(sku_request.sku_codes))
            if len(unique_codes) != len(sku_request.sku_codes):
                self.log_warning(
                    "Se encontraron códigos SKU duplicados, eliminando duplicados",
                    original_count=len(sku_request.sku_codes),
                    unique_count=len(unique_codes)
                )
            
            skus = await self.sku_repository.get_skus_by_codes(unique_codes)
            
            self.log_info(
                "SKUs obtenidos exitosamente",
                requested_count=len(unique_codes),
                found_count=len(skus)
            )
            
            return skus
            
        except ValueError as e:
            self.log_error(
                "Error de validación al obtener SKUs",
                error=e,
                sku_codes=sku_request.sku_codes
            )
            raise
            
        except Exception as e:
            self.log_error(
                "Error inesperado al obtener SKUs",
                error=e,
                sku_codes=sku_request.sku_codes
            )
            raise ValueError(f"Error al obtener SKUs: {str(e)}")
