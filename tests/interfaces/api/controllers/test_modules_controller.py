import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.interfaces.api.controllers.modules_controller import ModulesController
from app.core.response import SuccessResponse

class DummyRequest:
    state = MagicMock(user=MagicMock())

@pytest.mark.asyncio
async def test_get_active_module_users_success():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_active_module_users.return_value = {"user_emails": ["a@b.com"], "total_users": 1}
    response = await controller.get_active_module_users(request, use_cases)
    assert isinstance(response, SuccessResponse)
    assert response.data["user_emails"] == ["a@b.com"]

@pytest.mark.asyncio
async def test_get_active_module_users_exception():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_active_module_users.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_active_module_users(request, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_active_modules_success():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_active_modules.return_value = {"modules": ["mod1"], "total_modules": 1}
    response = await controller.get_active_modules(request, use_cases)
    assert isinstance(response, SuccessResponse)
    assert response.data["modules"] == ["mod1"]

@pytest.mark.asyncio
async def test_get_active_modules_exception():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_active_modules.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_active_modules(request, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_success():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_module_users_by_module_id.return_value = {"users": ["user1"], "total_users": 1, "module_id": 1}
    response = await controller.get_module_users_by_module_id(request, 1, use_cases)
    assert isinstance(response, SuccessResponse)
    assert response.data["users"] == ["user1"]
    assert response.data["module_id"] == 1

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_value_error():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_module_users_by_module_id.side_effect = ValueError("bad id")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_module_users_by_module_id(request, 0, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_get_module_users_by_module_id_exception():
    controller = ModulesController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_module_users_by_module_id.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_module_users_by_module_id(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
