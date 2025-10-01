import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.interfaces.api.controllers.master_data_controller import MasterDataController
from app.core.response import SuccessResponse

class DummyRequest:
    state = MagicMock(user=MagicMock())

@pytest.mark.asyncio
async def test_get_all_divisions_success():
    controller = MasterDataController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_all_divisions.return_value = [MagicMock()]
    response = await controller.get_all_divisions(request, use_cases)
    assert isinstance(response, SuccessResponse)
    assert isinstance(response.data, list)

@pytest.mark.asyncio
async def test_get_all_divisions_exception():
    controller = MasterDataController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_all_divisions.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_all_divisions(request, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
