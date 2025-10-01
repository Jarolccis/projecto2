from typing import List
from google.api_core import exceptions as google_exceptions
from google.cloud.exceptions import NotFound, Forbidden

from app.domain.entities.sku import Sku
from app.domain.repositories.sku_repository import SkuRepository
from app.infrastructure.bigquery.bigquery_loader import BigQueryLoader
from app.infrastructure.bigquery.bigquery_helper import BigQueryHelper
from app.infrastructure.mappers.sku_mappers import map_bigquery_results_to_skus
from app.core.config import settings
from app.core.logging import LoggerMixin
from app.utils.hashing import format_text_array_with_wildcard


class SkuRepository(SkuRepository, LoggerMixin):
    
    def __init__(self):
        self.log_info("Inicializando SKU Repository")
        
        self.query_loader = BigQueryLoader()
        
        self.bigquery_helper = BigQueryHelper()
        
        self.log_info("SKU Repository inicializado correctamente")
    
    async def get_skus_by_codes(self, sku_codes: List[str]) -> List[Sku]:
        self.log_info(
            "Iniciando consulta de SKUs desde BigQuery",
            sku_codes_count=len(sku_codes),
            sku_codes=sku_codes[:5]  
        )
        
        try:
           
            formatted_sku_codes = format_text_array_with_wildcard(sku_codes)
            
            self.log_info(
                "Códigos SKU formateados para LIKE ANY con wildcard",
                original_codes=sku_codes,
                formatted_codes=formatted_sku_codes
            )
            
            query = self.query_loader.load_query(
                "get_skus_by_codes",
                sku_codes=formatted_sku_codes
            )
            
            self.log_info("Consulta SQL completa generada", full_query=query)
            
            results = self.bigquery_helper.execute_query(query, timeout=60)
            
            self.log_info(
                "Consulta completada exitosamente", 
                total_skus=len(results)
            )
            
            skus = map_bigquery_results_to_skus(results, self)
            
            self.log_info(
                "SKUs mapeados exitosamente",
                mapped_skus=len(skus)
            )
            
            return skus
        except google_exceptions.DeadlineExceeded as e:
            self.log_error(
                "Timeout en consulta BigQuery para SKUs",
                error=e,
                operation="get_skus_by_codes"
            )
            raise Exception(f"Consulta de SKUs excedió el límite de tiempo: {str(e)}")
        except Forbidden as e:
            self.log_error(
                "Error de permisos en BigQuery para SKUs",
                error=e,
                operation="get_skus_by_codes"
            )
            raise Exception(f"Sin permisos para acceder a BigQuery: {str(e)}")
        except NotFound as e:
            self.log_error(
                "Recurso no encontrado en BigQuery para SKUs",
                error=e,
                operation="get_skus_by_codes"
            )
            raise Exception(f"Recurso de BigQuery no encontrado: {str(e)}")
        except Exception as e:
            self.log_error(
                "Error inesperado al consultar SKUs en BigQuery",
                error=e,
                operation="get_skus_by_codes",
                sku_codes=sku_codes
            )
            self.log_warning(
                "BigQuery no disponible, retornando lista vacía",
                sku_codes=sku_codes
            )
            return []
    
    
    def close(self) -> None:
        """Cierra el helper de BigQuery y libera recursos."""
        if hasattr(self, 'bigquery_helper'):
            self.bigquery_helper.close()
            self.log_info("BigQuery SKU Helper cerrado")
