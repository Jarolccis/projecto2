import pytest
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.repositories.modules_repository import ModulesRepository

def make_execute_mock(return_value):
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = return_value
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    return execute_mock

@pytest.mark.asyncio
async def test_get_active_module_users_success():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.return_value = make_execute_mock([])
    result = await repo.get_active_module_users()
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_get_active_modules_success():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.return_value = make_execute_mock([])
    result = await repo.get_active_modules()
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_success():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.return_value = make_execute_mock([])
    result = await repo.get_module_users_by_module_id(1)
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_get_active_module_users_db_error():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await repo.get_active_module_users()

@pytest.mark.asyncio
async def test_get_active_modules_db_error():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await repo.get_active_modules()

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_db_error():
    session = AsyncMock()
    repo = ModulesRepository(session)
    session.execute.side_effect = Exception("db error")
    with pytest.raises(Exception):
        await repo.get_module_users_by_module_id(1)
