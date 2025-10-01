
import pytest
from unittest.mock import AsyncMock, MagicMock
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
