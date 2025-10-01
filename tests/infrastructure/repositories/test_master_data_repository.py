import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.asyncio
@patch("app.infrastructure.repositories.master_data_repository.BigQueryLoader")
@patch("app.infrastructure.repositories.master_data_repository.BigQueryHelper")
def test_get_all_divisions_success(MockBigQueryHelper, MockBigQueryLoader):
    from app.infrastructure.repositories.master_data_repository import MasterDataRepository
    mock_loader = MockBigQueryLoader.return_value
    mock_helper = MockBigQueryHelper.return_value
    mock_loader.load_query.return_value = "SELECT * FROM divisions"
    mock_helper.execute_query.return_value = []
    repo = MasterDataRepository()
    repo._convert_division_results_to_entities = MagicMock(return_value=[])
    import asyncio
    result = asyncio.run(repo.get_all_divisions())
    assert isinstance(result, list)

@pytest.mark.asyncio
@patch("app.infrastructure.repositories.master_data_repository.BigQueryLoader")
@patch("app.infrastructure.repositories.master_data_repository.BigQueryHelper")
def test_get_all_divisions_exception(MockBigQueryHelper, MockBigQueryLoader):
    from app.infrastructure.repositories.master_data_repository import MasterDataRepository
    mock_loader = MockBigQueryLoader.return_value
    mock_helper = MockBigQueryHelper.return_value
    mock_loader.load_query.side_effect = Exception("fail")
    repo = MasterDataRepository()
    import asyncio
    with pytest.raises(Exception):
        asyncio.run(repo.get_all_divisions())
