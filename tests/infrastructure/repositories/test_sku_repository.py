
import pytest
from unittest.mock import AsyncMock, MagicMock, create_autospec
from app.infrastructure.repositories.sku_repository import SkuRepository

@pytest.mark.asyncio
async def test_get_skus_success():
    repo = create_autospec(SkuRepository, instance=True)
    repo.get_skus_by_codes = AsyncMock(return_value=[MagicMock(sku_code="SKU1"), MagicMock(sku_code="SKU2")])
    result = await repo.get_skus_by_codes(["SKU1", "SKU2"])
    assert [r.sku_code for r in result] == ["SKU1", "SKU2"]

@pytest.mark.asyncio
async def test_get_skus_error():
    repo = create_autospec(SkuRepository, instance=True)
    repo.get_skus_by_codes = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await repo.get_skus_by_codes(["SKU1"])
