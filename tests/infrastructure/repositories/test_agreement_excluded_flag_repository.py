import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.infrastructure.repositories.agreement_excluded_flag_repository import PostgresAgreementExcludedFlagRepository
from app.domain.entities.agreement_excluded_flag import AgreementExcludedFlag

@pytest.mark.asyncio
async def test_create_agreement_excluded_flag_success():
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    repo = PostgresAgreementExcludedFlagRepository(session)
    entity = AgreementExcludedFlag(
        id=None,
        agreement_id=1,
        excluded_flag_id=2,
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_at=None,
        updated_status_by_user_email="user@example.com",
        excluded_flag_name=None
    )
    # Mock model with id, created_at, updated_at
    mock_model = MagicMock(id=10, created_at="2024-01-01", updated_at="2024-01-02")
    with patch("app.infrastructure.repositories.agreement_excluded_flag_repository.AgreementExcludedFlagModel", return_value=mock_model):
        result = await repo.create_agreement_excluded_flag(entity)
        assert result.id == 10
        assert result.created_at == "2024-01-01"
        assert result.updated_at == "2024-01-02"

@pytest.mark.asyncio
async def test_create_agreement_excluded_flag_exception():
    session = MagicMock()
    session.flush = AsyncMock(side_effect=Exception("db error"))
    session.refresh = AsyncMock()
    repo = PostgresAgreementExcludedFlagRepository(session)
    entity = AgreementExcludedFlag(
        id=None,
        agreement_id=1,
        excluded_flag_id=2,
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_at=None,
        updated_status_by_user_email="user@example.com",
        excluded_flag_name=None
    )
    with patch("app.infrastructure.repositories.agreement_excluded_flag_repository.AgreementExcludedFlagModel"):
        with pytest.raises(Exception):
            await repo.create_agreement_excluded_flag(entity)

@pytest.mark.asyncio
async def test_get_agreement_excluded_flags_success():
    session = MagicMock()
    repo = PostgresAgreementExcludedFlagRepository(session)
    # Simula el resultado de session.execute(stmt)
    row = MagicMock(
        id=1,
        agreement_id=1,
        excluded_flag_id=2,
        active=True,
        created_at="2024-01-01",
        created_by_user_email="user@example.com",
        updated_at="2024-01-02",
        updated_status_by_user_email="user@example.com",
        excluded_flag_name="FlagName"
    )
    result_mock = MagicMock(fetchall=MagicMock(return_value=[row]))
    session.execute = AsyncMock(return_value=result_mock)
    flags = await repo.get_agreement_excluded_flags(1)
    assert len(flags) == 1
    assert flags[0].excluded_flag_name == "FlagName"

@pytest.mark.asyncio
async def test_get_agreement_excluded_flags_empty():
    session = MagicMock()
    repo = PostgresAgreementExcludedFlagRepository(session)
    result_mock = MagicMock(fetchall=MagicMock(return_value=[]))
    session.execute = AsyncMock(return_value=result_mock)
    flags = await repo.get_agreement_excluded_flags(1)
    assert flags == []
