import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.store_use_cases import StoresUseCases
from app.interfaces.schemas import StoreResponse
from datetime import datetime

class DummyStore:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.mark.asyncio
async def test_get_store_by_id_found():
    repo = AsyncMock()
    dummy_store = DummyStore(
        id=1,
        business_unit_id=2,
        store_id=3,
        name="TestStore",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        zone_id=4,
        zone_name="Zona",
        channel_id=5,
        channel_name="Canal"
    )
    repo.get_by_id.return_value = dummy_store
    use_cases = StoresUseCases(repo)
    result = await use_cases.get_store_by_id(3)
    assert isinstance(result, StoreResponse)
    assert result.id == 1
    assert result.name == "TestStore"

@pytest.mark.asyncio
async def test_get_store_by_id_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    use_cases = StoresUseCases(repo)
    result = await use_cases.get_store_by_id(99)
    assert result is None

@pytest.mark.asyncio
async def test_get_store_by_id_exception():
    repo = AsyncMock()
    repo.get_by_id.side_effect = Exception("fail")
    use_cases = StoresUseCases(repo)
    with pytest.raises(Exception):
        await use_cases.get_store_by_id(1)

@pytest.mark.asyncio
async def test_get_active_stores_success():
    repo = AsyncMock()
    dummy_store = DummyStore(id=1, name="Test", store_id=3)
    repo.get_active_stores.return_value = [dummy_store]
    use_cases = StoresUseCases(repo)
    stores = await use_cases.get_active_stores()
    assert len(stores) == 1
    assert stores[0]["name"] == "Test"

@pytest.mark.asyncio
async def test_get_active_stores_exception():
    repo = AsyncMock()
    repo.get_active_stores.side_effect = Exception("fail")
    use_cases = StoresUseCases(repo)
    with pytest.raises(Exception):
        await use_cases.get_active_stores()
