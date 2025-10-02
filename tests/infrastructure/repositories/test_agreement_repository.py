import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.repositories.agreement_repository import PostgresAgreementRepository
from app.domain.entities.agreement import Agreement
from app.core.agreement_enums import SourceSystemEnum
from datetime import date, datetime
from decimal import Decimal

@pytest.mark.asyncio
async def test_create_agreement_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    agreement = Agreement(
        id=None,
        business_unit_id=1,
        agreement_number=123,
        start_date=date.today(),
        end_date=date.today(),
        agreement_type_id="TYPE1",
        status_id="ACTIVE",
        rebate_type_id="REBATE",
        concept_id="CONCEPT",
        description="desc",
        activity_name="activity",
        source_system=SourceSystemEnum.SPF,
        spf_code="SPF001",
        spf_description="desc",
        currency_id=1,
        unit_price=Decimal("10.0"),
        billing_type="BILL",
        pmm_username="user",
        store_grouping_id="SG1",
        bulk_upload_document_id=None,
        active=True,
        created_at=datetime.now(),
        created_by_user_email="test@example.com",
        updated_at=datetime.now(),
        updated_status_by_user_email="test@example.com"
    )
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    async def refresh_side_effect(model):
        model.id = 1
    session.refresh.side_effect = refresh_side_effect
    result = await repo.create_agreement(agreement)
    assert agreement.id == 1

@pytest.mark.asyncio
async def test_create_agreement_exists():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    session.execute = AsyncMock()
    session.execute.return_value.scalar_one_or_none.return_value = 1
    exists = await repo.exists_agreement_by_number_and_business_unit(123, 1)
    assert exists is True

@pytest.mark.asyncio
async def test_create_agreement_not_exists():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    session.execute = AsyncMock()
    class DummyResult:
        def scalar_one_or_none(self):
            return None
    session.execute.return_value = DummyResult()
    exists = await repo.exists_agreement_by_number_and_business_unit(123, 1)
    assert exists is False

@pytest.mark.asyncio
async def test_get_agreement_by_id_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    # Simula resultado de execute().fetchone()
    result_mock = MagicMock()
    result_mock.fetchone = MagicMock(return_value=MagicMock(id=1))
    session.execute = AsyncMock(return_value=result_mock)
    with patch("app.infrastructure.repositories.agreement_repository.Agreement", autospec=True):
        agreement = await repo.get_agreement_by_id(1)
        assert agreement is not None

@pytest.mark.asyncio
async def test_get_agreement_by_id_exception():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    session.execute = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await repo.get_agreement_by_id(1)

@pytest.mark.asyncio
async def test_get_agreement_with_details_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    # Simula resultado de execute().fetchone()
    result_mock = MagicMock()
    result_mock.fetchone = MagicMock(return_value=MagicMock(id=1))
    session.execute = AsyncMock(return_value=result_mock)
    with patch("app.infrastructure.repositories.agreement_repository.Agreement", autospec=True):
        with patch.object(repo._product_repository, "get_agreement_products", AsyncMock(return_value=[])):
            with patch.object(repo._store_rule_repository, "get_agreement_store_rules", AsyncMock(return_value=[])):
                with patch.object(repo._excluded_flag_repository, "get_agreement_excluded_flags", AsyncMock(return_value=[])):
                    agreement, products, store_rules, excluded_flags = await repo.get_agreement_with_details(1)
                    assert agreement is not None
                    assert products == []
                    assert store_rules == []
                    assert excluded_flags == []

@pytest.mark.asyncio
async def test_create_agreement_product_delegates():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    with patch.object(repo._product_repository, "create_agreement_product", AsyncMock(return_value="ok")):
        result = await repo.create_agreement_product("p")
        assert result == "ok"

@pytest.mark.asyncio
async def test_create_agreement_store_rule_delegates():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    with patch.object(repo._store_rule_repository, "create_agreement_store_rule", AsyncMock(return_value="ok")):
        result = await repo.create_agreement_store_rule("s")
        assert result == "ok"

@pytest.mark.asyncio
async def test_create_agreement_excluded_flag_delegates():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    with patch.object(repo._excluded_flag_repository, "create_agreement_excluded_flag", AsyncMock(return_value="ok")):
        result = await repo.create_agreement_excluded_flag("e")
        assert result == "ok"

@pytest.mark.asyncio
async def test_create_complete_agreement_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    agreement = MagicMock()
    products = [MagicMock()]
    store_rules = [MagicMock()]
    excluded_flags = [MagicMock()]
    with patch.object(repo, "create_agreement", AsyncMock(return_value=agreement)):
        with patch.object(repo, "_create_agreement_products_bulk", AsyncMock(return_value=products)):
            with patch.object(repo, "_create_agreement_store_rules_bulk", AsyncMock(return_value=store_rules)):
                with patch.object(repo, "_create_agreement_excluded_flags_bulk", AsyncMock(return_value=excluded_flags)):
                    result = await repo.create_complete_agreement(agreement, products, store_rules, excluded_flags)
                    assert result[0] == agreement
                    assert result[1] == products
                    assert result[2] == store_rules
                    assert result[3] == excluded_flags

@pytest.mark.asyncio
async def test_update_complete_agreement_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    agreement_id = 1
    agreement = MagicMock()
    products = [MagicMock()]
    store_rules = [MagicMock()]
    excluded_flags = [MagicMock()]
    with patch.object(repo, "_update_agreement", AsyncMock(return_value=agreement)):
        with patch.object(repo, "_delete_agreement_products", AsyncMock()):
            with patch.object(repo, "_delete_agreement_store_rules", AsyncMock()):
                with patch.object(repo, "_delete_agreement_excluded_flags", AsyncMock()):
                    with patch.object(repo, "_create_agreement_products_bulk", AsyncMock(return_value=products)):
                        with patch.object(repo, "_create_agreement_store_rules_bulk", AsyncMock(return_value=store_rules)):
                            with patch.object(repo, "_create_agreement_excluded_flags_bulk", AsyncMock(return_value=excluded_flags)):
                                result = await repo.update_complete_agreement(agreement_id, agreement, products, store_rules, excluded_flags)
                                assert result[0] == agreement
                                assert result[1] == products
                                assert result[2] == store_rules
                                assert result[3] == excluded_flags

@pytest.mark.asyncio
async def test_search_agreements_success():
    session = AsyncMock()
    repo = PostgresAgreementRepository(session)
    with patch("app.infrastructure.repositories.agreement_repository.load_sql_query", return_value="SELECT ..."):
        session.execute = AsyncMock()
        result_mock = MagicMock()
        result_mock.fetchall = MagicMock(return_value=[])
        session.execute.return_value = result_mock
        with patch("app.infrastructure.repositories.agreement_repository.map_search_results_to_agreement_items", return_value=[]):
            from app.interfaces.schemas.agreement_schema import AgreementSearchRequest
            req = AgreementSearchRequest()
            result = await repo.search_agreements(req)
            assert hasattr(result, "agreements")
