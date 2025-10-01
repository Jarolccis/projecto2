import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.interfaces.api.controllers.lookups_controller import LookupController
from app.interfaces.schemas.lookup_schema import LookupValuesResponse, LookupValueSingleResponse

class DummyRequest:
    state = MagicMock(user=MagicMock())

def make_lookup_value_result():
    mock = MagicMock()
    mock.lookup_value_id = 1
    mock.option_key = "key"
    mock.display_value = "Display"
    mock.option_value = "VAL123"
    mock.metadata = {}
    mock.sort_order = 1
    mock.parent_id = None
    return mock

@pytest.mark.asyncio
async def test_get_lookup_values_by_category_success():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_lookup_values_by_category.return_value = [make_lookup_value_result()]
    # category_code debe ser válido según el schema (por ejemplo, alfanumérico y mayúsculas)
    response = await controller.get_lookup_values_by_category(request, "CAT123", use_cases)
    assert isinstance(response, LookupValuesResponse)
    assert response.count == 1

@pytest.mark.asyncio
async def test_get_lookup_values_by_category_value_error():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_lookup_values_by_category.side_effect = ValueError("bad category")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_lookup_values_by_category(request, "CAT123", use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_get_lookup_values_by_category_exception():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_lookup_values_by_category.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_lookup_values_by_category(request, "CAT123", use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_specific_lookup_value_success():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_specific_lookup_value.return_value = make_lookup_value_result()
    response = await controller.get_specific_lookup_value(request, "CAT123", "VAL123", use_cases)
    assert isinstance(response, LookupValueSingleResponse)
    # Accede directamente al campo de datos esperado
    # Ajusta 'data' si tu modelo usa otro nombre
    assert hasattr(response, "data")
    assert hasattr(response.data, "lookup_value_id")

@pytest.mark.asyncio
async def test_get_specific_lookup_value_not_found():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_specific_lookup_value.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_specific_lookup_value(request, "CAT123", "VAL123", use_cases)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_specific_lookup_value_value_error():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_specific_lookup_value.side_effect = ValueError("bad input")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_specific_lookup_value(request, "CAT123", "VAL123", use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_get_specific_lookup_value_exception():
    controller = LookupController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_specific_lookup_value.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_specific_lookup_value(request, "CAT123", "VAL123", use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
