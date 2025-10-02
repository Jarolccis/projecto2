import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status, UploadFile
from app.interfaces.api.controllers.agreements_bulk_upload_controller import AgreementsBulkUploadController
from app.core.agreement_enums import AgreementBulkUploadStatusEnum

class DummyRequest:
    state = type("obj", (), {"user": type("User", (), {"email": "test@example.com"})()})

@pytest.mark.asyncio
async def test_upload_bulk_agreements_success():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    file = MagicMock(spec=UploadFile)
    file.filename = "test.xlsx"
    use_cases = AsyncMock()
    # El valor correcto para que success sea True
    result = MagicMock(final_status=AgreementBulkUploadStatusEnum.PARTIAL_LOADED.value, document_id=1, valid_rows=1, invalid_rows=0)
    use_cases.process_bulk_upload.return_value = result
    with patch("app.interfaces.schemas.agreements_bulk_upload_schema.BulkUploadRequest"):
        response = await controller.upload_bulk_agreements(request, file, "PMM", use_cases)
        assert response.success is True
        assert response.data == result

@pytest.mark.asyncio
async def test_upload_bulk_agreements_invalid_file():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    use_cases = AsyncMock()
    with patch("app.interfaces.schemas.agreements_bulk_upload_schema.BulkUploadRequest"):
        with pytest.raises(HTTPException) as excinfo:
            await controller.upload_bulk_agreements(request, file, "PMM", use_cases)
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_upload_bulk_agreements_value_error():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    file = MagicMock(spec=UploadFile)
    file.filename = "test.xlsx"
    use_cases = AsyncMock()
    use_cases.process_bulk_upload.side_effect = ValueError("error")
    with patch("app.interfaces.schemas.agreements_bulk_upload_schema.BulkUploadRequest"):
        with pytest.raises(HTTPException) as excinfo:
            await controller.upload_bulk_agreements(request, file, "PMM", use_cases)
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_upload_bulk_agreements_exception():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    file = MagicMock(spec=UploadFile)
    file.filename = "test.xlsx"
    use_cases = AsyncMock()
    use_cases.process_bulk_upload.side_effect = Exception("fail")
    with patch("app.interfaces.schemas.agreements_bulk_upload_schema.BulkUploadRequest"):
        with pytest.raises(HTTPException) as excinfo:
            await controller.upload_bulk_agreements(request, file, "PMM", use_cases)
        assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_get_bulk_upload_document_success():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_document_by_id.return_value = MagicMock()
    response = await controller.get_bulk_upload_document(request, 1, use_cases)
    assert response.success is True

@pytest.mark.asyncio
async def test_get_bulk_upload_document_value_error():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_bulk_upload_document(request, 0, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_get_bulk_upload_document_not_found():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_document_by_id.side_effect = Exception("not found")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_bulk_upload_document(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_bulk_upload_document_exception():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_document_by_id.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.get_bulk_upload_document(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_resolve_bulk_upload_document_success():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    mock_data = MagicMock(agreements_creation_success=True, agreements_created=1, resolution_success=True, resolution_message="ok")
    use_cases.resolve_document_data.return_value = mock_data
    response = await controller.resolve_bulk_upload_document(request, 1, use_cases)
    assert response.success is True

@pytest.mark.asyncio
async def test_resolve_bulk_upload_document_value_error():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    with pytest.raises(HTTPException) as excinfo:
        await controller.resolve_bulk_upload_document(request, 0, use_cases)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_resolve_bulk_upload_document_not_found():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.resolve_document_data.side_effect = Exception("not found")
    with pytest.raises(HTTPException) as excinfo:
        await controller.resolve_bulk_upload_document(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_resolve_bulk_upload_document_exception():
    controller = AgreementsBulkUploadController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.resolve_document_data.side_effect = Exception("fail")
    with pytest.raises(HTTPException) as excinfo:
        await controller.resolve_bulk_upload_document(request, 1, use_cases)
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
