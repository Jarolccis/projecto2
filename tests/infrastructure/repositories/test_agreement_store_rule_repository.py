import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.infrastructure.repositories.agreement_store_rule_repository import PostgresAgreementStoreRuleRepository
from app.domain.entities.agreement_store_rule import AgreementStoreRule

@pytest.mark.asyncio
async def test_create_agreement_store_rule_success():
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    repo = PostgresAgreementStoreRuleRepository(session)
    entity = AgreementStoreRule(
        id=None,
        agreement_id=1,
        store_id=2,
        status="INCLUDE",
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at=None,
        store_name=None
    )
    mock_model = MagicMock(id=10, created_at="2024-01-01", updated_at="2024-01-02")
    with patch("app.infrastructure.repositories.agreement_store_rule_repository.AgreementStoreRuleModel", return_value=mock_model):
        result = await repo.create_agreement_store_rule(entity)
        assert result.id == 10
        assert result.created_at == "2024-01-01"
        assert result.updated_at == "2024-01-02"

@pytest.mark.asyncio
async def test_create_agreement_store_rule_exception():
    session = MagicMock()
    session.flush = AsyncMock(side_effect=Exception("db error"))
    session.refresh = AsyncMock()
    repo = PostgresAgreementStoreRuleRepository(session)
    entity = AgreementStoreRule(
        id=None,
        agreement_id=1,
        store_id=2,
        status="INCLUDE",
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at=None,
        store_name=None
    )
    with patch("app.infrastructure.repositories.agreement_store_rule_repository.AgreementStoreRuleModel"):
        with pytest.raises(Exception):
            await repo.create_agreement_store_rule(entity)

@pytest.mark.asyncio
async def test_get_agreement_store_rules_success():
    session = MagicMock()
    repo = PostgresAgreementStoreRuleRepository(session)
    row = MagicMock(
        id=1,
        agreement_id=1,
        store_id=2,
        status="INCLUDE",
        active=True,
        created_at="2024-01-01",
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at="2024-01-02",
        store_name="StoreName"
    )
    result_mock = MagicMock(fetchall=MagicMock(return_value=[row]))
    session.execute = AsyncMock(return_value=result_mock)
    rules = await repo.get_agreement_store_rules(1)
    assert len(rules) == 1
    assert rules[0].store_name == "StoreName"

@pytest.mark.asyncio
async def test_get_agreement_store_rules_exception():
    session = MagicMock()
    session.execute = AsyncMock(side_effect=Exception("fail"))
    repo = PostgresAgreementStoreRuleRepository(session)
    with pytest.raises(Exception):
        await repo.get_agreement_store_rules(1)

@pytest.mark.asyncio
async def test_exists_agreement_store_rule_true():
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=1)
    session.execute = AsyncMock(return_value=result_mock)
    repo = PostgresAgreementStoreRuleRepository(session)
    exists = await repo.exists_agreement_store_rule(1, 2)
    assert exists is True

@pytest.mark.asyncio
async def test_exists_agreement_store_rule_false():
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    session.execute = AsyncMock(return_value=result_mock)
    repo = PostgresAgreementStoreRuleRepository(session)
    exists = await repo.exists_agreement_store_rule(1, 2)
    assert exists is False

@pytest.mark.asyncio
async def test_exists_agreement_store_rule_exception():
    session = MagicMock()
    session.execute = AsyncMock(side_effect=Exception("fail"))
    repo = PostgresAgreementStoreRuleRepository(session)
    with pytest.raises(Exception):
        await repo.exists_agreement_store_rule(1, 2)
