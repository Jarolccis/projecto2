import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from app.interfaces.api.controllers.agreements_controller import AgreementController
from app.interfaces.schemas.agreement_schema import AgreementCreateRequest, AgreementCreateResponse, AgreementSearchRequest, AgreementUpdateRequest, AgreementDetailResponse
from app.core.agreement_enums import SourceSystemEnum
from app.core.response import SuccessResponse, PaginatedResponse
from datetime import date, datetime

class DummyRequest:
    state = type("obj", (), {"user": type("User", (), {"bu_id": 1, "email": "test@example.com"})()})

class DummyAgreement:
    def __init__(self):
        self.id = 1
        self.business_unit_id = 1
        self.agreement_number = 1
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
        self.currency_id = 1
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
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = AgreementCreateRequest(
        business_unit_id=1,
        agreement_type_id="TYPE1",
        source_system=SourceSystemEnum.SPF,
        rebate_type_id="REBATE",
        concept_id="CONCEPT",
        unit_price=10.0,
        billing_type="BILL",
        description="desc",
        status_id="ACTIVE",
        products=[{"product_id": 1, "sku_code": "SKU1", "rebate_value": 1.0, "rebate_type_id": "REBATE", "active": True}],
        store_rules=[],
        excluded_flags=[]
    )
    use_cases = AsyncMock()
    use_cases.create_agreement.return_value = DummyAgreement()
    response = await controller.create_agreement(request, agreement_data, use_cases)
    assert response is not None

@pytest.mark.asyncio
async def test_create_agreement_value_error():
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = MagicMock()
    use_cases = AsyncMock()
    use_cases.create_agreement.side_effect = ValueError("Invalid data")
    with pytest.raises(HTTPException) as excinfo:
        await controller.create_agreement(request, agreement_data, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_create_agreement_exception():
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = MagicMock()
    use_cases = AsyncMock()
    use_cases.create_agreement.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.create_agreement(request, agreement_data, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_search_agreements_success():
    controller = AgreementController()
    request = DummyRequest()
    search_request = AgreementSearchRequest()
    use_cases = AsyncMock()
    # Simula un resultado de búsqueda
    mock_result = MagicMock()
    mock_result.total_count = 1
    mock_result.agreements = [MagicMock()]
    use_cases.search_agreements.return_value = mock_result
    response = await controller.search_agreements(request, search_request, use_cases)
    assert response is not None
    assert response.pagination["total"] == 1

@pytest.mark.asyncio
async def test_search_agreements_value_error():
    controller = AgreementController()
    request = DummyRequest()
    search_request = AgreementSearchRequest()
    use_cases = AsyncMock()
    use_cases.search_agreements.side_effect = ValueError("Invalid search")
    with pytest.raises(HTTPException) as excinfo:
        await controller.search_agreements(request, search_request, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_search_agreements_exception():
    controller = AgreementController()
    request = DummyRequest()
    search_request = AgreementSearchRequest()
    use_cases = AsyncMock()
    use_cases.search_agreements.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.search_agreements(request, search_request, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_agreement_by_id_success():
    controller = AgreementController()
    request = DummyRequest()
    use_cases = AsyncMock()
    mock_detail = MagicMock(products=[], store_rules=[], excluded_flags=[])
    use_cases.get_agreement_by_id.return_value = mock_detail
    response = await controller.get_agreement_by_id(request, 1, use_cases)
    assert response is not None

@pytest.mark.asyncio
async def test_get_agreement_by_id_value_error():
    controller = AgreementController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_agreement_by_id.side_effect = ValueError("Not found")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_agreement_by_id(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_agreement_by_id_exception():
    controller = AgreementController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_agreement_by_id.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_agreement_by_id(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_update_agreement_success():
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = MagicMock()
    use_cases = AsyncMock()
    mock_agreement = MagicMock(id=1, business_unit_id=1)
    use_cases.update_agreement.return_value = mock_agreement
    response = await controller.update_agreement(request, 1, agreement_data, use_cases)
    assert response == mock_agreement

@pytest.mark.asyncio
async def test_update_agreement_value_error():
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = MagicMock()
    use_cases = AsyncMock()
    use_cases.update_agreement.side_effect = ValueError("Invalid update")
    with pytest.raises(HTTPException) as excinfo:
        await controller.update_agreement(request, 1, agreement_data, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_update_agreement_exception():
    controller = AgreementController()
    request = DummyRequest()
    agreement_data = MagicMock()
    use_cases = AsyncMock()
    use_cases.update_agreement.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.update_agreement(request, 1, agreement_data, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
