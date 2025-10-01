import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.master_data_use_cases import MasterDataUseCases

@pytest.mark.asyncio
async def test_get_all_divisions_success():
    repo = AsyncMock()
    # Simula un dict con los campos esperados por DivisionResponse
    repo.get_all_divisions.return_value = [{
        "division_id": 1,
        "division_code": "D01",
        "division_name": "Division Test"
    }]
    use_cases = MasterDataUseCases(repo)
    result = await use_cases.get_all_divisions()
    assert isinstance(result, list)
    assert result[0].division_id == 1
    assert result[0].division_code == "D01"
    assert result[0].division_name == "Division Test"

@pytest.mark.asyncio
async def test_get_all_divisions_exception():
    repo = AsyncMock()
    repo.get_all_divisions.side_effect = Exception("fail")
    use_cases = MasterDataUseCases(repo)
    with pytest.raises(Exception):
        await use_cases.get_all_divisions()
