import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.infrastructure.repositories.stores_repository import StoresRepository, _to_entity

class DummyModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.mark.asyncio
async def test_get_by_id_found():
    session = AsyncMock()
    dummy_model = DummyModel(id=1, business_unit_id=2, store_id=3, name="Test", zone_id=4, zone_name="Z", channel_id=5, channel_name="C", is_active=True, created_at=None, updated_at=None)
    session.get.return_value = dummy_model
    repo = StoresRepository(session)
    result = await repo.get_by_id(3)
    assert result.id == 1
    assert result.name == "Test"

@pytest.mark.asyncio
async def test_get_by_id_not_found():
    session = AsyncMock()
    session.get.return_value = None
    repo = StoresRepository(session)
    result = await repo.get_by_id(99)
    assert result is None

@pytest.mark.asyncio
async def test_get_by_id_db_error():
    session = AsyncMock()
    session.get.side_effect = SQLAlchemyError("fail")
    repo = StoresRepository(session)
    with pytest.raises(SQLAlchemyError):
        await repo.get_by_id(1)

@pytest.mark.asyncio
async def test_get_active_stores_success():
    session = AsyncMock()
    dummy_model = DummyModel(id=1, business_unit_id=2, store_id=3, name="Test", zone_id=4, zone_name="Z", channel_id=5, channel_name="C", is_active=True, created_at=None, updated_at=None)
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [dummy_model]
    session.execute.return_value = result_mock
    repo = StoresRepository(session)
    stores = await repo.get_active_stores()
    assert len(stores) == 1
    assert stores[0].name == "Test"

@pytest.mark.asyncio
async def test_get_active_stores_db_error():
    session = AsyncMock()
    session.execute.side_effect = SQLAlchemyError("fail")
    repo = StoresRepository(session)
    with pytest.raises(SQLAlchemyError):
        await repo.get_active_stores()
