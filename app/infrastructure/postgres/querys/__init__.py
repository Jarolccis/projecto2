"""SQL query files for PostgreSQL operations."""

import os
from pathlib import Path


def load_sql_query(query_name: str) -> str:
    """Load SQL query from file.
    
    Args:
        query_name: Name of the SQL file without extension
        
    Returns:
        SQL query content as string
        
    Raises:
        FileNotFoundError: If the query file doesn't exist
    """
    queries_dir = Path(__file__).parent
    query_file = queries_dir / f"{query_name}.sql"
    
    if not query_file.exists():
        raise FileNotFoundError(f"SQL query file not found: {query_file}")
    
    with open(query_file, 'r', encoding='utf-8') as f:
        return f.read()


# Available queries
AVAILABLE_QUERIES = [
    "search_agreements",
    # Add more query names as they are created
]

__all__ = ["load_sql_query", "AVAILABLE_QUERIES"]
