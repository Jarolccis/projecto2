import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.lookup_use_cases import LookupUseCases
from app.domain.entities.lookup import LookupValueResult

def make_lookup_value_result():
    mock = MagicMock(spec=LookupValueResult)
    mock.lookup_value_id = 1
    mock.option_key = "key"
    mock.display_value = "Display"
    mock.option_value = "opt"
    mock.metadata = {}
    mock.sort_order = 1
    mock.parent_id = None
    return mock

@pytest.mark.asyncio
async def test_get_lookup_values_by_category_success():
    repo = AsyncMock()
    repo.get_values_by_category_code.return_value = [make_lookup_value_result()]
    use_cases = LookupUseCases(repo)
    class DummyRequest:
        category_code = "cat"
    result = await use_cases.get_lookup_values_by_category(DummyRequest())
    assert isinstance(result, list)
    assert hasattr(result[0], "lookup_value_id")

@pytest.mark.asyncio
async def test_get_lookup_values_by_category_exception():
    repo = AsyncMock()
    repo.get_values_by_category_code.side_effect = Exception("fail")
    use_cases = LookupUseCases(repo)
    class DummyRequest:
        category_code = "cat"
    with pytest.raises(Exception):
        await use_cases.get_lookup_values_by_category(DummyRequest())

@pytest.mark.asyncio
async def test_get_specific_lookup_value_success():
    repo = AsyncMock()
    repo.get_value_by_category_and_option.return_value = make_lookup_value_result()
    use_cases = LookupUseCases(repo)
    class DummyRequest:
        category_code = "cat"
        option_value = "opt"
    result = await use_cases.get_specific_lookup_value(DummyRequest())
    assert result is not None
    assert hasattr(result, "lookup_value_id")

@pytest.mark.asyncio
async def test_get_specific_lookup_value_none():
    repo = AsyncMock()
    repo.get_value_by_category_and_option.return_value = None
    use_cases = LookupUseCases(repo)
    class DummyRequest:
        category_code = "cat"
        option_value = "opt"
    result = await use_cases.get_specific_lookup_value(DummyRequest())
    assert result is None

@pytest.mark.asyncio
async def test_get_specific_lookup_value_exception():
    repo = AsyncMock()
    repo.get_value_by_category_and_option.side_effect = Exception("fail")
    use_cases = LookupUseCases(repo)
    class DummyRequest:
        category_code = "cat"
        option_value = "opt"
    with pytest.raises(Exception):
        await use_cases.get_specific_lookup_value(DummyRequest())
