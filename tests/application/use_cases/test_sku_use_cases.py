import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.sku_use_cases import SkuUseCases

class DummyUser:
    bu_id = 1
    email = "test@example.com"

@pytest.mark.asyncio
async def test_get_skus_success():
    repo = AsyncMock()
    use_cases = SkuUseCases(repo)
    repo.get_skus_by_codes.return_value = ["SKU1", "SKU2"]
    user = DummyUser()
    # Llamar al método real de la clase, que usa get_skus_by_codes
    result = await use_cases.get_skus_by_codes(type('SkuCodesRequest', (), {'sku_codes': ["SKU1", "SKU2"]})())
    assert result == ["SKU1", "SKU2"]

@pytest.mark.asyncio
async def test_get_skus_error():
    repo = AsyncMock()
    use_cases = SkuUseCases(repo)
    repo.get_skus_by_codes.side_effect = Exception("fail")
    user = DummyUser()
    with pytest.raises(Exception):
        await use_cases.get_skus_by_codes(type('SkuCodesRequest', (), {'sku_codes': ["SKU1"]})())
