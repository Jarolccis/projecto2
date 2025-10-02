
import pytest
@pytest.mark.asyncio
async def test_validate_agreement_business_rules_duplicate_number():
    class Repo(AsyncMock):
        async def exists_agreement_by_number_and_business_unit(self, number, bu):
            return True
    use_cases = AgreementUseCases(Repo())
    agreement_data = DummyAgreement()
    agreement_data.agreement_number = "A-001"
    agreement_data.business_unit_id = 1
    with pytest.raises(ValueError):
        await use_cases._validate_agreement_business_rules(agreement_data)

@pytest.mark.asyncio
async def test_validate_agreement_business_rules_success():
    class Repo(AsyncMock):
        async def exists_agreement_by_number_and_business_unit(self, number, bu):
            return False
    use_cases = AgreementUseCases(Repo())
    agreement_data = DummyAgreement()
    agreement_data.agreement_number = "A-002"
    agreement_data.business_unit_id = 1
    await use_cases._validate_agreement_business_rules(agreement_data)

@pytest.mark.asyncio
async def test_build_agreement_response_error():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    with pytest.raises(AttributeError):
        await use_cases._build_agreement_response(None, None, None, None)

@pytest.mark.asyncio
async def test_search_agreements_value_error_limit():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    req = AsyncMock()
    req.limit = 2000
    req.offset = 0
    req.division_codes = req.status_ids = req.created_by_emails = req.agreement_number = req.sku_code = req.description = req.rebate_type_id = req.concept_id = req.spf_code = req.spf_description = req.supplier_ruc = req.supplier_name = req.store_grouping_id = req.pmm_username = None
    with pytest.raises(ValueError):
        await use_cases.search_agreements(req)

@pytest.mark.asyncio
async def test_search_agreements_value_error_offset():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    req = AsyncMock()
    req.limit = 10
    req.offset = -1
    req.division_codes = req.status_ids = req.created_by_emails = req.agreement_number = req.sku_code = req.description = req.rebate_type_id = req.concept_id = req.spf_code = req.spf_description = req.supplier_ruc = req.supplier_name = req.store_grouping_id = req.pmm_username = None
    with pytest.raises(ValueError):
        await use_cases.search_agreements(req)

@pytest.mark.asyncio
async def test_search_agreements_success():
    repo = AsyncMock()
    repo.search_agreements.return_value = AsyncMock(total_count=1, agreements=[1])
    use_cases = AgreementUseCases(repo)
    req = AsyncMock()
    req.limit = 10
    req.offset = 0
    req.division_codes = req.status_ids = req.created_by_emails = req.agreement_number = req.sku_code = req.description = req.rebate_type_id = req.concept_id = req.spf_code = req.spf_description = req.supplier_ruc = req.supplier_name = req.store_grouping_id = req.pmm_username = None
    result = await use_cases.search_agreements(req)
    assert result.total_count == 1

@pytest.mark.asyncio
async def test_get_agreement_by_id_not_found():
    repo = AsyncMock()
    repo.get_agreement_with_details.return_value = None
    use_cases = AgreementUseCases(repo)
    with pytest.raises(ValueError):
        await use_cases.get_agreement_by_id(123)

@pytest.mark.asyncio
async def test_update_agreement_not_found():
    repo = AsyncMock()
    repo.get_agreement_by_id.return_value = None
    use_cases = AgreementUseCases(repo)
    agreement_data = DummyAgreement()
    user = DummyUser()
    with pytest.raises(ValueError):
        await use_cases.update_agreement(1, agreement_data, user)

@pytest.mark.asyncio
async def test_validate_agreement_business_rules_for_update_duplicate_products():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    agreement_data = AsyncMock()
    agreement_data.products = [AsyncMock(sku_code="A"), AsyncMock(sku_code="A")]
    agreement_data.store_rules = []
    agreement_data.excluded_flags = []
    with pytest.raises(ValueError):
        await use_cases._validate_agreement_business_rules_for_update(1, agreement_data)

@pytest.mark.asyncio
async def test_validate_agreement_business_rules_for_update_duplicate_flags():
    repo = AsyncMock()
    use_cases = AgreementUseCases(repo)
    agreement_data = AsyncMock()
    agreement_data.products = []
    agreement_data.store_rules = []
    agreement_data.excluded_flags = [AsyncMock(excluded_flag_id=1), AsyncMock(excluded_flag_id=1)]
    with pytest.raises(ValueError):
        await use_cases._validate_agreement_business_rules_for_update(1, agreement_data)


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
