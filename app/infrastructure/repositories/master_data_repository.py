"""BigQuery master data repository implementation."""

from typing import Any, Dict, List, Optional

from google.api_core import exceptions as google_exceptions

from app.domain.entities.division import Division
from app.domain.repositories.master_data_repository import MasterDataRepository
from app.infrastructure.bigquery.bigquery_helper import BigQueryHelper
from app.infrastructure.bigquery.bigquery_loader import BigQueryLoader
from app.core.config import settings
from app.core.logging import LoggerMixin


class MasterDataRepository(MasterDataRepository, LoggerMixin):
    """BigQuery master data repository implementation."""
    
    def __init__(self):
        """Initialize the BigQuery master data repository."""
        self.log_info("Initializing BigQuery Master Data Repository")
        
        # Initialize the query loader
        self.query_loader = BigQueryLoader()
        
        # Initialize the BigQuery helper
        self.bigquery_helper = BigQueryHelper()
        
        self.log_info("BigQuery Master Data Repository initialized successfully")
    
    async def get_all_divisions(self) -> List[Division]:
        """Get all divisions from BigQuery."""
        self.log_info("Starting divisions query from BigQuery")
        
        try:
            # Load the query from the SQL file
            query = self.query_loader.load_query(
                "get_division_query",
                project_id=settings.gcp_project_id
            )
            
            self.log_debug("Divisions SQL query loaded", query_preview=query[:100])
            
            # Execute the query using the helper
            results = self.bigquery_helper.execute_query(query, timeout=60)
            
            self.log_info(
                "Divisions query completed successfully", 
                total_divisions=len(results)
            )
            
            # Convert results to domain entities
            divisions = self._convert_division_results_to_entities(results)
            
            return divisions
            
        except google_exceptions.Timeout as e:
            self.log_error(
                "Timeout in BigQuery query for divisions", 
                error=e,
                operation="get_all_divisions"
            )
            raise Exception(f"Divisions query exceeded time limit: {str(e)}")
        except google_exceptions.PermissionDenied as e:
            self.log_error(
                "Permission error in BigQuery for divisions", 
                error=e,
                operation="get_all_divisions"
            )
            raise Exception(f"No permissions to access BigQuery: {str(e)}")
        except google_exceptions.NotFound as e:
            self.log_error(
                "Resource not found in BigQuery for divisions", 
                error=e,
                operation="get_all_divisions"
            )
            raise Exception(f"BigQuery resource not found: {str(e)}")
        except Exception as e:
            self.log_error(
                "Unexpected error querying divisions in BigQuery", 
                error=e,
                operation="get_all_divisions"
            )
            raise Exception(f"Error getting divisions: {str(e)}")
    
    def _convert_division_results_to_entities(self, results: List) -> List[Division]:
        """Convert BigQuery results to Division entities."""
        divisions = []
        conversion_errors = 0
        
        for row in results:
            try:
                division = Division(
                    division_id=int(row.division_id) if row.division_id else 0,
                    division_code=str(row.division_code) if row.division_code else "",
                    division_name=str(row.division_name) if row.division_name else ""
                )
                divisions.append(division)
            except Exception as e:
                conversion_errors += 1
                self.log_warning(
                    "Error converting division row to entity", 
                    error_message=str(e),
                    row_data=str(row)
                )
                continue
        
        self.log_debug(
            "Division results conversion completed", 
            total_results=len(results),
            successful_conversions=len(divisions),
            conversion_errors=conversion_errors
        )
        return divisions
    
    def close(self) -> None:
        """Close the BigQuery helper and release resources."""
        if hasattr(self, 'bigquery_helper'):
            self.bigquery_helper.close()
            self.log_info("BigQuery Master Data Helper closed")
