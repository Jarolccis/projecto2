"""BigQuery helper for configuration and connection management."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core import exceptions as google_exceptions

from app.core.config import settings
from app.core.logging import LoggerMixin

# Constantes de configuración
DEFAULT_HTTP_TIMEOUT = 30
DEFAULT_CONNECTION_POOL_SIZE = 10
DEFAULT_QUERY_TIMEOUT = 60
DEFAULT_VALIDATION_TIMEOUT = 10
QUERY_PREVIEW_LENGTH = 100

# Campos requeridos para credenciales de service account
REQUIRED_CREDENTIAL_FIELDS = ['type', 'project_id', 'private_key', 'client_email']

# Scope mínimo necesario para BigQuery
BIGQUERY_SCOPE = "https://www.googleapis.com/auth/bigquery"


class BigQueryHelper(LoggerMixin):
    """Helper class for BigQuery configuration and connection management."""
    
    def __init__(self) -> None:
        """Inicializa el helper de BigQuery."""
        self.credentials: Optional[service_account.Credentials] = None
        self.client: Optional[bigquery.Client] = None
        self._setup_credentials()
        self._setup_bigquery_client()
    
    def _setup_credentials(self) -> None:
        """Configura las credenciales de Google Cloud.
        
        Raises:
            FileNotFoundError: Si el archivo de credenciales no existe
            ValueError: Si el archivo de credenciales es inválido
            Exception: Para otros errores inesperados
        """
        try:
            key_file_path = Path(settings.gcp_key_file)
            
            # Validar existencia y tipo de archivo
            if not key_file_path.exists():
                raise FileNotFoundError(f"Archivo de credenciales no encontrado: {key_file_path}")
            
            if not key_file_path.is_file():
                raise ValueError(f"La ruta especificada no es un archivo: {key_file_path}")
            
            # Leer y validar el archivo de credenciales
            with open(key_file_path, 'r', encoding='utf-8') as key_file:
                service_account_info = json.load(key_file)
            
            # Validar estructura del JSON
            self._validate_credentials_structure(service_account_info)
            
            # Crear credenciales
            self.credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=[BIGQUERY_SCOPE]
            )
            
            self.log_info(
                "Credenciales configuradas exitosamente", 
                project_id=service_account_info.get('project_id'),
                key_file_path=str(key_file_path)
            )
            
        except FileNotFoundError as e:
            self.log_error(
                "Error de archivo al configurar credenciales", 
                error=e,
                key_file_path=str(Path(settings.gcp_key_file))
            )
            raise
        except json.JSONDecodeError as e:
            self.log_error(
                "Error de formato JSON en credenciales", 
                error=e,
                key_file_path=str(Path(settings.gcp_key_file))
            )
            raise ValueError(f"Archivo de credenciales con formato JSON inválido: {key_file_path}")
        except Exception as e:
            self.log_error(
                "Error inesperado al configurar credenciales", 
                error=e
            )
            raise
    
    def _validate_credentials_structure(self, credentials: Dict[str, Any]) -> None:
        """Valida la estructura de las credenciales.
        
        Args:
            credentials: Diccionario con las credenciales
            
        Raises:
            ValueError: Si faltan campos requeridos
        """
        missing_fields = [field for field in REQUIRED_CREDENTIAL_FIELDS if field not in credentials]
        
        if missing_fields:
            self.log_error(
                "Campos requeridos faltantes en credenciales", 
                missing_fields=missing_fields,
                available_fields=list(credentials.keys())
            )
            raise ValueError(f"Campos requeridos faltantes en credenciales: {missing_fields}")
    
    def _setup_bigquery_client(self) -> None:
        """Configura el cliente de BigQuery con opciones optimizadas.
        
        Raises:
            Exception: Para errores inesperados durante la configuración
        """
        try:
            if not self.credentials:
                raise Exception("Credenciales no configuradas")
            
            # Crear cliente con opciones optimizadas
            self.client = bigquery.Client(
                credentials=self.credentials,
                project=settings.gcp_project_id
            )
            
            # Configurar opciones adicionales
            self._configure_client_options()
            
            self.log_info(
                "Cliente BigQuery configurado exitosamente", 
                project_id=settings.gcp_project_id
            )
            
        except Exception as e:
            self.log_error(
                "Error al configurar cliente BigQuery", 
                error=e
            )
            raise
    
    def _configure_client_options(self) -> None:
        """Configura opciones adicionales del cliente BigQuery."""
        if not hasattr(self.client, '_http'):
            self.log_warning("No se puede configurar opciones HTTP del cliente BigQuery")
            return
        
        try:
            # Configurar timeout HTTP
            if hasattr(self.client._http, 'timeout'):
                self.client._http.timeout = DEFAULT_HTTP_TIMEOUT
            
            # Configurar pool de conexiones
            if hasattr(self.client._http, 'pool'):
                self.client._http.pool.maxsize = DEFAULT_CONNECTION_POOL_SIZE
                self.log_debug(f"Pool de conexiones configurado con tamaño máximo: {DEFAULT_CONNECTION_POOL_SIZE}")
            
            self.log_debug(f"Timeout HTTP configurado: {DEFAULT_HTTP_TIMEOUT}s")
            
        except Exception as e:
            self.log_warning(f"No se pudieron configurar todas las opciones del cliente: {e}")
    
    def execute_query(self, query: str, timeout: int = DEFAULT_QUERY_TIMEOUT) -> List[Any]:
        """Ejecuta una consulta SQL en BigQuery.
        
        Args:
            query: Consulta SQL a ejecutar
            timeout: Timeout en segundos para la consulta
            
        Returns:
            Lista de resultados de la consulta
            
        Raises:
            google_exceptions.Timeout: Si la consulta excede el timeout
            google_exceptions.PermissionDenied: Si no hay permisos
            google_exceptions.NotFound: Si el recurso no existe
            Exception: Para otros errores
        """
        try:
            query_preview = query[:QUERY_PREVIEW_LENGTH] + "..." if len(query) > QUERY_PREVIEW_LENGTH else query
            self.log_debug(f"Ejecutando consulta SQL: {query_preview}")
            
            # Ejecutar la consulta
            query_job = self.client.query(query)
            query_job.result(timeout=timeout)
            
            # Obtener resultados
            results = list(query_job.result())
            
            self.log_info(
                "Consulta completada exitosamente", 
                total_rows=len(results)
            )
            
            return results
            
        except google_exceptions.Timeout as e:
            self.log_error(f"Timeout en consulta BigQuery: {e}")
            raise
        except google_exceptions.PermissionDenied as e:
            self.log_error(f"Error de permisos en BigQuery: {e}")
            raise
        except google_exceptions.NotFound as e:
            self.log_error(f"Recurso no encontrado en BigQuery: {e}")
            raise
        except Exception as e:
            self.log_error(f"Error inesperado al consultar BigQuery: {e}")
            raise
    
    def get_query_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un job de consulta específico.
        
        Args:
            job_id: ID del job de consulta
            
        Returns:
            Diccionario con información del job o None si no se encuentra
        """
        try:
            job = self.client.get_job(job_id)
            return {
                'job_id': job.job_id,
                'state': job.state,
                'created': job.created,
                'started': job.started,
                'ended': job.ended,
                'total_bytes_processed': getattr(job, 'total_bytes_processed', None),
                'total_rows': getattr(job, 'total_rows', None)
            }
        except Exception as e:
            self.log_warning(f"Error al obtener estadísticas de consulta: {e}")
            return None
    
    def validate_connection(self) -> bool:
        """Valida la conexión a BigQuery ejecutando una consulta simple.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            if not self.client:
                self.log_error("Cliente BigQuery no está configurado")
                return False
            
            # Ejecutar consulta simple de validación
            query = "SELECT 1 as test"
            results = self.execute_query(query, timeout=DEFAULT_VALIDATION_TIMEOUT)
            
            if results and len(results) > 0:
                self.log_info("Conexión a BigQuery validada correctamente")
                return True
            else:
                self.log_warning("Conexión a BigQuery no retornó resultados esperados")
                return False
                
        except Exception as e:
            self.log_error(f"Error al validar conexión a BigQuery: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """Obtiene información del proyecto de BigQuery.
        
        Returns:
            Diccionario con información del proyecto
        """
        try:
            if not self.client:
                self.log_error("Cliente BigQuery no está configurado")
                return {}
            
            project = self.client.project
            dataset_ref = self.client.dataset('_INFORMATION_SCHEMA', project=project)
            
            return {
                'project_id': project,
                'dataset_count': len(list(self.client.list_datasets())),
                'location': getattr(self.client, 'location', 'unknown')
            }
        except Exception as e:
            self.log_error(f"Error al obtener información del proyecto: {e}")
            return {}
    
    def close(self) -> None:
        """Cierra el cliente de BigQuery y libera recursos."""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.log_info("Cliente BigQuery cerrado")
        except Exception as e:
            self.log_warning(f"Error al cerrar cliente BigQuery: {e}")
    
    def __enter__(self) -> 'BigQueryHelper':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
