import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.modules_use_cases import ModulesUseCases
from app.domain.entities.module import Module, ModuleUser
from datetime import datetime

@pytest.mark.asyncio
async def test_get_active_module_users_success():
    repo = AsyncMock()
    repo.get_active_module_users.return_value = ["a@b.com"]
    use_cases = ModulesUseCases(repo)
    result = await use_cases.get_active_module_users()
    assert result.user_emails == ["a@b.com"]
    assert result.total_users == 1

@pytest.mark.asyncio
async def test_get_active_module_users_exception():
    repo = AsyncMock()
    repo.get_active_module_users.side_effect = Exception("fail")
    use_cases = ModulesUseCases(repo)
    with pytest.raises(Exception):
        await use_cases.get_active_module_users()

@pytest.mark.asyncio
async def test_get_active_modules_success():
    repo = AsyncMock()
    now = datetime.utcnow()
    module = Module(id=1, business_unit_id=1, name="mod1", description="desc", is_active=True, created_at=now, updated_at=now)
    repo.get_active_modules.return_value = [module]
    use_cases = ModulesUseCases(repo)
    result = await use_cases.get_active_modules()
    assert result.modules[0].name == "mod1"
    assert result.total_modules == 1

@pytest.mark.asyncio
async def test_get_active_modules_exception():
    repo = AsyncMock()
    repo.get_active_modules.side_effect = Exception("fail")
    use_cases = ModulesUseCases(repo)
    with pytest.raises(Exception):
        await use_cases.get_active_modules()

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_success():
    repo = AsyncMock()
    now = datetime.utcnow()
    user = ModuleUser(id=1, user_email="user1@x.com", module_id=1, created_at=now, updated_at=now)
    repo.get_module_users_by_module_id.return_value = [user]
    use_cases = ModulesUseCases(repo)
    class DummyRequest:
        module_id = 1
    result = await use_cases.get_module_users_by_module_id(DummyRequest())
    assert result.users[0].user_email == "user1@x.com"
    assert result.module_id == 1
    assert result.total_users == 1

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_exception():
    repo = AsyncMock()
    repo.get_module_users_by_module_id.side_effect = Exception("fail")
    use_cases = ModulesUseCases(repo)
    class DummyRequest:
        module_id = 1
    with pytest.raises(Exception):
        await use_cases.get_module_users_by_module_id(DummyRequest())
