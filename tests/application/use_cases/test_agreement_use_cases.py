

import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.agreement_use_cases import AgreementUseCases
from app.core.agreement_enums import SourceSystemEnum
from datetime import date, datetime

class DummyUser:
    bu_id = 1
    email = "test@example.com"

    def __init__(self):
        self.id = 1
        self.business_unit_id = 1
        self.agreement_number = "A-001"
        self.start_date = date.today()
        self.end_date = date.today()
        self.agreement_type_id = "TYPE1"
        self.status_id = "ACTIVE"
        self.rebate_type_id = "REBATE"
        self.concept_id = "CONCEPT"
        self.description = "desc"
        self.activity_name = "activity"
        self.source_system = SourceSystemEnum.SPF
        self.spf_code = "SPF001"
        self.spf_description = "desc"
        self.currency_id = "PEN"
        self.unit_price = 10.0
        self.billing_type = "BILL"
        self.pmm_username = "user"
        self.store_grouping_id = "SG1"
        self.active = True
        self.created_at = datetime.now().isoformat()
        self.created_by_user_email = "test@example.com"
        self.updated_at = datetime.now().isoformat()
        self.updated_status_by_user_email = "test@example.com"
        self.products = []
        self.store_rules = []
        self.excluded_flags = []


class DummyAgreement:
    def __init__(self):
        from app.core.agreement_enums import SourceSystemEnum
        from datetime import date, datetime
        self.id = 1
        self.business_unit_id = 1
        self.agreement_number = 123
        self.start_date = date.today()
        self.end_date = date.today()
        self.agreement_type_id = "TYPE1"
        self.status_id = "ACTIVE"
        self.rebate_type_id = "REBATE"
        self.concept_id = "CONCEPT"
        self.description = "desc"
        self.activity_name = "activity"
        self.source_system = SourceSystemEnum.SPF
        self.spf_code = "SPF001"
        self.spf_description = "desc"
        self.currency_id = "PEN"
        self.unit_price = 10.0
        self.billing_type = "BILL"
        self.pmm_username = "user"
        self.store_grouping_id = "SG1"
        self.active = True
        self.created_at = datetime.now().isoformat()
        self.created_by_user_email = "test@example.com"
        self.updated_at = datetime.now().isoformat()
        self.updated_status_by_user_email = "test@example.com"
        self.products = []
        self.store_rules = []
        self.excluded_flags = []

@pytest.mark.asyncio
async def test_create_agreement_success():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    agreement_data = DummyAgreement()
    user = DummyUser()
    repo.create_complete_agreement.return_value = (DummyAgreement(), [], [], [])
    use_cases._build_agreement_response = AsyncMock(return_value=DummyAgreement())
    response = await use_cases.create_agreement(agreement_data, user)
    assert response.id == 1

@pytest.mark.asyncio
async def test_create_agreement_value_error():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    agreement_data = DummyAgreement()
    user = DummyUser()
    repo.create_complete_agreement.side_effect = ValueError("Invalid data")
    with pytest.raises(ValueError):
        await use_cases.create_agreement(agreement_data, user)

@pytest.mark.asyncio
async def test_create_agreement_exception():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    agreement_data = DummyAgreement()
    user = DummyUser()
    repo.create_complete_agreement.side_effect = Exception("fail")
    with pytest.raises(Exception):
        await use_cases.create_agreement(agreement_data, user)
