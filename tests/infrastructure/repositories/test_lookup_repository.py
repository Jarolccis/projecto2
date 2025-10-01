import pytest
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.repositories.lookup_repository import PostgresLookupRepository
from app.domain.entities.lookup import LookupValueResult

def make_lookup_value_result():
    mock = MagicMock(spec=LookupValueResult)
    mock.lookup_value_id = 1
    mock.option_key = "key"
    mock.display_value = "Display"
    mock.option_value = "VAL123"
    mock.metadata = {}
    mock.sort_order = 1
    mock.parent_id = None
    return mock

@pytest.mark.asyncio
async def test_get_values_by_category_code_success():
    session = AsyncMock()
    repo = PostgresLookupRepository(session)
    
    # Crear mock row con todos los atributos requeridos
    mock_row = MagicMock()
    mock_row.lookup_value_id = 1
    mock_row.option_key = "key"
    mock_row.display_value = "display"
    mock_row.option_value = "value"
    mock_row.metadata = {}
    mock_row.sort_order = 1
    mock_row.parent_id = None
    
    # Configurar correctamente los mocks asíncronos
    execute_result = MagicMock()
    execute_result.all.return_value = [mock_row]  # No usar AsyncMock aquí
    session.execute.return_value = execute_result
    
    repo.log_info = MagicMock()
    repo.log_error = MagicMock()
    
    result = await repo.get_values_by_category_code("CAT123")
    assert isinstance(result, list)
    assert len(result) > 0
    assert hasattr(result[0], "lookup_value_id")

@pytest.mark.asyncio
async def test_get_values_by_category_code_db_error():
    session = AsyncMock()
    repo = PostgresLookupRepository(session)
    session.execute.side_effect = Exception("db error")
    repo.log_error = MagicMock()
    
    with pytest.raises(Exception):
        await repo.get_values_by_category_code("CAT123")

@pytest.mark.asyncio
async def test_get_value_by_category_and_option_success():
    session = AsyncMock()
    repo = PostgresLookupRepository(session)
    
    # Crear mock row
    mock_row = MagicMock()
    mock_row.lookup_value_id = 1
    mock_row.option_key = "key"
    mock_row.display_value = "display"
    mock_row.option_value = "value"
    mock_row.metadata = {}
    mock_row.sort_order = 1
    mock_row.parent_id = None
    
    # Configurar mocks correctamente
    execute_result = MagicMock()
    execute_result.first.return_value = mock_row  # No usar AsyncMock aquí
    session.execute.return_value = execute_result
    
    repo.log_info = MagicMock()
    repo.log_error = MagicMock()
    
    result = await repo.get_value_by_category_and_option("CAT123", "VAL123")
    assert result is not None
    assert hasattr(result, "lookup_value_id")

@pytest.mark.asyncio
async def test_get_value_by_category_and_option_none():
    session = AsyncMock()
    repo = PostgresLookupRepository(session)
    
    # Configurar mocks para retornar None
    execute_result = MagicMock()
    execute_result.first.return_value = None  # No usar AsyncMock aquí
    session.execute.return_value = execute_result
    
    repo.log_info = MagicMock()
    repo.log_error = MagicMock()
    
    result = await repo.get_value_by_category_and_option("CAT123", "VAL123")
    assert result is None

@pytest.mark.asyncio
async def test_get_value_by_category_and_option_db_error():
    session = AsyncMock()
    repo = PostgresLookupRepository(session)
    session.execute.side_effect = Exception("db error")
    repo.log_error = MagicMock()
    
    with pytest.raises(Exception):
        await repo.get_value_by_category_and_option("CAT123", "VAL123")