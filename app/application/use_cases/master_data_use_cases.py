"""Master data use cases implementing business logic."""

from typing import List

from app.interfaces.schemas.division_schema import DivisionResponse
from app.domain.repositories.master_data_repository import MasterDataRepository
from app.core.logging import LoggerMixin


class MasterDataUseCases(LoggerMixin):
    """Casos de uso para datos maestros."""

    def __init__(self, master_data_repository: MasterDataRepository):
        self._master_data_repository = master_data_repository
        self.log_info(
            "MasterDataUseCases inicializado", 
            repository_type=type(master_data_repository).__name__
        )

    async def get_all_divisions(self) -> List[DivisionResponse]:
        """Obtiene todas las divisiones."""
        try:
            self.log_info("Iniciando obtención de todas las divisiones")
            
            divisions = await self._master_data_repository.get_all_divisions()
            
            self.log_info(
                "Divisiones obtenidas exitosamente", 
                total_divisions=len(divisions)
            )
            
            # Convertir entidades de dominio a schemas de respuesta
            division_responses = [
                DivisionResponse.model_validate(division) 
                for division in divisions
            ]
            
            return division_responses
            
        except Exception as e:
            self.log_error(
                "Error al obtener divisiones", 
                error=e
            )
            raise