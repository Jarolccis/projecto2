from typing import List
from app.domain.entities.sku import Sku
from app.core.logging import LoggerMixin
import logging

logger = logging.getLogger(__name__)


def map_bigquery_result_to_sku(row, logger_instance: LoggerMixin = None) -> Sku:
    try:
        sku = Sku.create(
            sku=str(row.Sku) if hasattr(row, 'Sku') and row.Sku else "",
            descripcion_sku=str(row.DescripcionSku) if hasattr(row, 'DescripcionSku') and row.DescripcionSku else "",
            costo_reposicion=float(row.CostoReposicion) if hasattr(row, 'CostoReposicion') and row.CostoReposicion else 0.0,
            estado_id=int(row.EstadoId) if hasattr(row, 'EstadoId') and row.EstadoId else 0,
            marca_id=int(row.MarcaId) if hasattr(row, 'MarcaId') and row.MarcaId else 0,
            marca=str(row.Marca) if hasattr(row, 'Marca') and row.Marca else "",
            subclase_id=int(row.SubClaseId) if hasattr(row, 'SubClaseId') and row.SubClaseId else 0,
            codigo_subclase=str(row.CodigoSubClase) if hasattr(row, 'CodigoSubClase') and row.CodigoSubClase else "",
            subclase=str(row.SubClase) if hasattr(row, 'SubClase') and row.SubClase else "",
            clase_id=int(row.ClaseId) if hasattr(row, 'ClaseId') and row.ClaseId else 0,
            codigo_clase=str(row.CodigoClase) if hasattr(row, 'CodigoClase') and row.CodigoClase else "",
            clase=str(row.Clase) if hasattr(row, 'Clase') and row.Clase else "",
            subdepartamento_id=int(row.SubDepartamentoId) if hasattr(row, 'SubDepartamentoId') and row.SubDepartamentoId else 0,
            codigo_subdepartamento=str(row.CodigoSubDepartamento) if hasattr(row, 'CodigoSubDepartamento') and row.CodigoSubDepartamento else "",
            subdepartamento=str(row.SubDepartamento) if hasattr(row, 'SubDepartamento') and row.SubDepartamento else "",
            departamento_id=int(row.DepartamentoId) if hasattr(row, 'DepartamentoId') and row.DepartamentoId else 0,
            codigo_departamento=str(row.CodigoDepartamento) if hasattr(row, 'CodigoDepartamento') and row.CodigoDepartamento else "",
            departamento=str(row.Departamento) if hasattr(row, 'Departamento') and row.Departamento else "",
            division_id=int(row.DivisionId) if hasattr(row, 'DivisionId') and row.DivisionId else 0,
            codigo_division=str(row.CodigoDivision) if hasattr(row, 'CodigoDivision') and row.CodigoDivision else "",
            division=str(row.Division) if hasattr(row, 'Division') and row.Division else "",
            proveedor_id=int(row.ProveedorId) if hasattr(row, 'ProveedorId') and row.ProveedorId else 0,
            ruc_proveedor=str(row.RucProveedor) if hasattr(row, 'RucProveedor') and row.RucProveedor else "",
            proveedor=str(row.Proveedor) if hasattr(row, 'Proveedor') and row.Proveedor else "",
        )
        return sku
        
    except Exception as e:
        if logger_instance:
            logger_instance.log_warning(
                "Error al mapear fila de SKU",
                error_message=str(e),
                row_data=str(row)
            )
        else:
            logger.warning(f"Error al mapear fila de SKU: {e}, row_data: {str(row)}")
        raise


def map_bigquery_results_to_skus(results: List, logger_instance: LoggerMixin = None) -> List[Sku]:
    skus = []
    conversion_errors = 0
    
    for row in results:
        try:
            sku = map_bigquery_result_to_sku(row, logger_instance)
            skus.append(sku)
            
        except Exception as e:
            conversion_errors += 1
            if logger_instance:
                logger_instance.log_warning(
                    "Error al mapear fila de SKU",
                    error_message=str(e),
                    row_data=str(row)
                )
            else:
                logger.warning(f"Error al mapear fila de SKU: {e}, row_data: {str(row)}")
            continue
    
    if logger_instance:
        logger_instance.log_debug(
            "Mapeo de resultados de SKUs completado",
            total_results=len(results),
            successful_conversions=len(skus),
            conversion_errors=conversion_errors
        )
    else:
        logger.debug(f"Mapeo de resultados de SKUs completado - Total: {len(results)}, Exitosos: {len(skus)}, Errores: {conversion_errors}")
    
    return skus
