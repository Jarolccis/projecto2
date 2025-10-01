"""BigQuery query loader utility."""

import os
from pathlib import Path
from typing import Dict, Any

from app.core.logging import LoggerMixin


class BigQueryLoader(LoggerMixin):
    """Utilitario para cargar consultas SQL desde archivos."""
    
    def __init__(self, queries_dir: str = None):
        """Inicializa el cargador de consultas."""
        if queries_dir is None:
            # Ruta por defecto relativa a este archivo
            current_dir = Path(__file__).parent
            self.queries_dir = current_dir / "querys"
        else:
            self.queries_dir = Path(queries_dir)
        
        self.log_info(
            "BigQueryLoader inicializado", 
            queries_directory=str(self.queries_dir)
        )
    
    def load_query(self, query_name: str, **kwargs) -> str:
        """Carga una consulta SQL desde un archivo y reemplaza parámetros.
        
        Args:
            query_name: Nombre del archivo SQL (sin extensión)
            **kwargs: Parámetros para reemplazar en la consulta
            
        Returns:
            Consulta SQL procesada
            
        Raises:
            FileNotFoundError: Si no se encuentra el archivo de consulta
        """
        try:
            self.log_info(
                "Cargando consulta SQL", 
                query_name=query_name,
                parameters=kwargs
            )
            
            query_file = self.queries_dir / f"{query_name}.sql"
            
            if not query_file.exists():
                self.log_error(
                    "Archivo de consulta no encontrado", 
                    query_name=query_name,
                    file_path=str(query_file),
                    queries_directory=str(self.queries_dir)
                )
                raise FileNotFoundError(f"Archivo de consulta no encontrado: {query_file}")
            
            # Leer el contenido del archivo
            with open(query_file, 'r', encoding='utf-8') as f:
                query_content = f.read()
            
            # Reemplazar parámetros en la consulta
            processed_query = query_content.format(**kwargs)
            
            self.log_info(
                "Consulta SQL cargada exitosamente", 
                query_name=query_name,
                file_path=str(query_file),
                content_length=len(processed_query),
                parameters_replaced=len(kwargs)
            )
            
            return processed_query
            
        except FileNotFoundError:
            raise
        except Exception as e:
            self.log_error(
                "Error inesperado al cargar consulta SQL", 
                error=e,
                query_name=query_name,
                file_path=str(self.queries_dir / f"{query_name}.sql")
            )
            raise
    
    def get_available_queries(self) -> list:
        """Obtiene la lista de consultas disponibles."""
        try:
            if not self.queries_dir.exists():
                self.log_warning(
                    "Directorio de consultas no existe", 
                    queries_directory=str(self.queries_dir)
                )
                return []
            
            sql_files = list(self.queries_dir.glob("*.sql"))
            available_queries = [f.stem for f in sql_files]
            
            self.log_info(
                "Consultas disponibles obtenidas", 
                total_queries=len(available_queries),
                queries_directory=str(self.queries_dir)
            )
            
            return available_queries
            
        except Exception as e:
            self.log_error(
                "Error al obtener consultas disponibles", 
                error=e,
                queries_directory=str(self.queries_dir)
            )
            return []
