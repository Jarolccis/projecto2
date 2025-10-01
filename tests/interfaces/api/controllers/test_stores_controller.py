import pytest
from fastapi import HTTPException
from app.interfaces.api.controllers.stores_controller import StoresController
from app.interfaces.schemas import SuccessResponse, StoreResponse

class DummyLogger(StoresController):
    def __init__(self):
        super().__init__()
        self.logged = []
    def log_info(self, msg, **kwargs):
        self.logged.append(("info", msg, kwargs))
    def log_error(self, msg, error=None, **kwargs):
        self.logged.append(("error", msg, error, kwargs))
    def log_warning(self, msg, **kwargs):
        self.logged.append(("warning", msg, kwargs))

class DummyUseCases:
    async def get_active_stores(self):
        return [{"id": 1, "name": "Store1"}]

    async def get_store_by_id(self, store_id):
        if store_id == 1:
            return {"id": 1, "name": "Store1"}
        return None

class DummyRequest:
    state = type("obj", (), {"user": "dummy_user"})

@pytest.mark.asyncio
async def test_get_active_stores_success():
    controller = StoresController()
    request = DummyRequest()
    use_cases = DummyUseCases()
    response = await controller.get_active_stores(request, use_cases)
    assert isinstance(response, SuccessResponse)
    assert response.data == [{"id": 1, "name": "Store1"}]

@pytest.mark.asyncio
async def test_get_store_by_id_success():
    controller = StoresController()
    request = DummyRequest()
    use_cases = DummyUseCases()
    response = await controller.get_store_by_id(request, 1, use_cases)
    assert isinstance(response, SuccessResponse)
    assert response.data == {"id": 1, "name": "Store1"}

@pytest.mark.asyncio
async def test_get_store_by_id_not_found():
    controller = StoresController()
    request = DummyRequest()
    use_cases = DummyUseCases()
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_store_by_id(request, 999, use_cases)
    assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_get_store_by_id_invalid_id():
    controller = StoresController()
    request = DummyRequest()
    use_cases = DummyUseCases()
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_store_by_id(request, 0, use_cases)
    assert excinfo.value.status_code == 400

# Test error handling in get_active_stores
@pytest.mark.asyncio
async def test_get_active_stores_exception():
    class FailingUseCases:
        async def get_active_stores(self):
            raise Exception("DB error")
    controller = DummyLogger()
    request = DummyRequest()
    use_cases = FailingUseCases()
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_active_stores(request, use_cases)
    assert excinfo.value.status_code == 500
    assert any(l[0] == "error" for l in controller.logged)

# Test error handling in get_store_by_id (unexpected exception)
@pytest.mark.asyncio
async def test_get_store_by_id_unexpected_exception():
    class FailingUseCases:
        async def get_store_by_id(self, store_id):
            raise Exception("DB error")
    controller = DummyLogger()
    request = DummyRequest()
    use_cases = FailingUseCases()
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_store_by_id(request, 1, use_cases)
    assert excinfo.value.status_code == 500
    assert any(l[0] == "error" for l in controller.logged)
