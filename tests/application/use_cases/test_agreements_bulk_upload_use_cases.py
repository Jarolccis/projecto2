import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.agreements_bulk_upload_use_cases import AgreementsBulkUploadUseCases
from app.domain.repositories.agreements_bulk_upload_repository import AgreementsBulkUploadRepository
from app.core.utils.excel_processing import ExcelProcessing
from app.domain.repositories.sku_repository import SkuRepository
import types
from fastapi import UploadFile
from app.core.agreement_enums import SourceSystemEnum
from app.interfaces.schemas.agreements_bulk_upload_schema import BulkUploadRequest, BulkUploadProcessResponse, TemplateDownloadResponse
from app.domain.entities.agreements_bulk_upload import AgreementsBulkUploadDocument, AgreementsBulkUploadDocumentRow
from app.interfaces.schemas.security_schema import User

# DummyRepo base para herencia en los tests
class DummyRepo(AgreementsBulkUploadRepository):
    async def create_document(self, document): pass
    async def get_document_by_id(self, document_id): pass
    async def get_document_by_uid(self, document_uid): pass
    async def create_document_rows(self, rows): pass
    async def get_document_rows(self, document_id): pass
    async def update_document_status(self, document_id, status_id, comments=None): pass
    async def validate_document_rows(self, document_id, valid_skus=None): pass
    async def resolve_document_rows(self, document_id, resolved_by_user_email): pass
    async def create_agreements_from_resolved_rows(self, document_id, created_by_user_email, skus): pass
    async def get_document_with_rows(self, document_id): pass

class DummySkuRepo(SkuRepository):
    async def get_skus_by_codes(self, sku_codes): return []

class DummyExcel(ExcelProcessing):
    pass

class DummyUser:
    bu_id = 1
    email = "test@example.com"
    country = "PE"

from uuid import uuid4, UUID
from datetime import datetime
class DummyDoc:
    def __init__(self):
        self.id = 1
        self.business_unit_id = 1
        self.status_id = "PROGRESS"  # Cambiado de "IN_PROGRESS" a "PROGRESS" (10 caracteres)
        self.full_path_document = "/tmp/dummy.xlsx"
        self.comments = None
        self.document_uid = uuid4()  # UUID type
        self.source_system = SourceSystemEnum.SPF
        self.created_at = datetime(2025, 10, 1, 0, 0, 0)
        self.created_by_user_email = "test@example.com"
        self.updated_at = datetime(2025, 10, 1, 0, 0, 0)
    # Ensure __dict__ property for Pydantic compatibility
    @property
    def __dict__(self):
        return {
            'id': self.id,
            'business_unit_id': self.business_unit_id,
            'status_id': self.status_id,
            'full_path_document': self.full_path_document,
            'comments': self.comments,
            'document_uid': self.document_uid,
            'source_system': self.source_system,
            'created_at': self.created_at,
            'created_by_user_email': self.created_by_user_email,
            'updated_at': self.updated_at
        }

class DummyRow:
    sku = "SKU1"
    pmm_user = group_name = excluded_flags = included_stores = excluded_stores = rebate_type = concept = note = spf_code = spf_description = sku
    start_date = end_date = unit_rebate_pen = billing_type = observations = "x"

class DummyExcelService(ExcelProcessing):
    async def validate_excel_file(self, file): return True
    async def get_excel_sheets(self, file): return ["Plantilla SPF"]
    async def process_excel_file(self, **kwargs): return ([{"sku": "SKU1"}], [])
    async def create_excel_from_data(self, **kwargs): return b"excel"

class DummyRepoFull(DummyRepo):
    async def create_document(self, document): return DummyDoc()
    async def create_document_rows(self, rows): return rows
    async def validate_document_rows(self, doc_id, valid_skus=None): return (True, "ok")
    async def update_document_status(self, *a, **k): pass
    async def get_document_by_id(self, doc_id): return DummyDoc()
    async def get_document_rows(self, doc_id): return [DummyRow()]
    async def get_document_with_rows(self, doc_id): return (DummyDoc(), [DummyRow()])
    async def resolve_document_rows(self, document_id, resolved_by_user_email): return (True, "ok")
    async def create_agreements_from_resolved_rows(self, document_id, created_by_user_email, skus): return (True, "msg", 1)

class DummyRepoNoRows(DummyRepoFull):
    async def get_document_rows(self, doc_id): return []
    async def get_document_with_rows(self, doc_id): return (DummyDoc(), [])

class DummyRepoNotFound(DummyRepoFull):
    async def get_document_by_id(self, doc_id): return None
    async def get_document_with_rows(self, doc_id): return (None, [])

class DummySkuRepoOk(SkuRepository):
    async def get_skus_by_codes(self, sku_codes):
        class Sku: sku = "SKU1"
        return [Sku()]

def make_request(source=SourceSystemEnum.SPF):
    req = BulkUploadRequest(source_system_type=source)
    return req

@pytest.mark.asyncio
async def test_process_bulk_upload_invalid_excel():
    class Excel(ExcelProcessing):
        async def validate_excel_file(self, file): return False
        async def get_excel_sheets(self, file): return []
        async def process_excel_file(self, **kwargs): return ([], [])
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), Excel(), DummySkuRepoOk())
    req = make_request()
    file = MagicMock(spec=UploadFile)
    file.filename = "dummy.xlsx"
    user = DummyUser()
    result = await usecase.process_bulk_upload(req, file, user)
    assert result.processing_status == "INVALID_FILE_FORMAT"

@pytest.mark.asyncio
async def test_process_bulk_upload_format_error():
    class Excel(ExcelProcessing):
        async def validate_excel_file(self, file): return True
        async def get_excel_sheets(self, file): return ["Plantilla SPF"]
        async def process_excel_file(self, **kwargs): return ([{"sku": "SKU1"}], ["error"])
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), Excel(), DummySkuRepoOk())
    req = make_request()
    file = MagicMock(spec=UploadFile)
    file.filename = "dummy.xlsx"
    user = DummyUser()
    result = await usecase.process_bulk_upload(req, file, user)
    assert result.processing_status == "FORMAT_VALIDATION_FAILED"

@pytest.mark.asyncio
async def test_process_bulk_upload_no_rows():
    usecase = AgreementsBulkUploadUseCases(DummyRepoNoRows(), DummyExcelService(), DummySkuRepoOk())
    req = make_request()
    file = MagicMock(spec=UploadFile)
    file.filename = "dummy.xlsx"
    user = DummyUser()
    result = await usecase.process_bulk_upload(req, file, user)
    assert result.processing_status == "COMPLETED"

@pytest.mark.asyncio
async def test_process_bulk_upload_exception():
    class Repo(DummyRepoFull):
        async def create_document(self, document): raise Exception("fail")
    usecase = AgreementsBulkUploadUseCases(Repo(), DummyExcelService(), DummySkuRepoOk())
    req = make_request()
    file = MagicMock(spec=UploadFile)
    user = DummyUser()
    with pytest.raises(Exception):
        await usecase.process_bulk_upload(req, file, user)

@pytest.mark.asyncio
async def test_get_document_by_id_success():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    result = await usecase.get_document_by_id(1)
    assert result.document.id == 1

@pytest.mark.asyncio
async def test_get_document_by_id_not_found():
    usecase = AgreementsBulkUploadUseCases(DummyRepoNotFound(), DummyExcelService(), DummySkuRepoOk())
    with pytest.raises(ValueError):
        await usecase.get_document_by_id(1)

@pytest.mark.asyncio
async def test_resolve_document_data_success():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    result = await usecase.resolve_document_data(1, user)
    assert result.resolution_success is True

@pytest.mark.asyncio
async def test_resolve_document_data_not_found():
    usecase = AgreementsBulkUploadUseCases(DummyRepoNotFound(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    with pytest.raises(ValueError):
        await usecase.resolve_document_data(1, user)

@pytest.mark.asyncio
async def test_resolve_document_data_create_agreements_fail():
    class Repo(DummyRepoFull):
        async def create_agreements_from_resolved_rows(self, document_id, created_by_user_email, skus): return (False, "fail", 0)
    usecase = AgreementsBulkUploadUseCases(Repo(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    result = await usecase.resolve_document_data(1, user)
    assert result.agreements_creation_success is False

@pytest.mark.asyncio
async def test_get_template_download_url_success():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    result = await usecase.get_template_download_url("SPF", user)
    assert isinstance(result, TemplateDownloadResponse)

@pytest.mark.asyncio
async def test_get_template_download_url_invalid_type():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    with pytest.raises(ValueError):
        await usecase.get_template_download_url("INVALID", user)

@pytest.mark.asyncio
async def test_get_document_rows_download_url_success():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    result = await usecase.get_document_rows_download_url(1, user)
    assert isinstance(result, TemplateDownloadResponse)

@pytest.mark.asyncio
async def test_get_document_rows_download_url_not_found():
    usecase = AgreementsBulkUploadUseCases(DummyRepoNotFound(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    with pytest.raises(ValueError):
        await usecase.get_document_rows_download_url(1, user)

@pytest.mark.asyncio
async def test_get_document_rows_download_url_no_rows():
    usecase = AgreementsBulkUploadUseCases(DummyRepoNoRows(), DummyExcelService(), DummySkuRepoOk())
    user = DummyUser()
    with pytest.raises(ValueError):
        await usecase.get_document_rows_download_url(1, user)

def test_get_column_configuration_spf():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    config = usecase._get_column_configuration(SourceSystemEnum.SPF)
    assert config[2] == "Plantilla SPF"

def test_get_column_configuration_pmm():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    config = usecase._get_column_configuration(SourceSystemEnum.PMM)
    assert config[2] == "Plantilla PMM"

def test_get_column_configuration_invalid():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    with pytest.raises(ValueError):
        usecase._get_column_configuration("INVALID")

import asyncio
def test_create_excel_from_rows_spf():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    doc = DummyDoc()
    doc.source_system = SourceSystemEnum.SPF
    rows = [DummyRow()]
    result = asyncio.run(usecase._create_excel_from_rows(rows, doc))
    assert result == b"excel"

def test_create_excel_from_rows_pmm():
    usecase = AgreementsBulkUploadUseCases(DummyRepoFull(), DummyExcelService(), DummySkuRepoOk())
    doc = DummyDoc()
    doc.source_system = SourceSystemEnum.PMM
    rows = [DummyRow()]
    result = asyncio.run(usecase._create_excel_from_rows(rows, doc))
    assert result == b"excel"

@pytest.mark.asyncio
async def test_process_bulk_upload_success():
    repo = DummyRepo()
    excel = DummyExcel()
    sku_repo = DummySkuRepo()
    usecase = AgreementsBulkUploadUseCases(repo, excel, sku_repo)
    usecase.process_bulk_upload = AsyncMock(return_value=MagicMock(document_id=1, valid_rows=10, invalid_rows=0, final_status="PARTIAL_LOADED"))
    result = await usecase.process_bulk_upload(request=MagicMock(), file=MagicMock(), user=MagicMock())
    assert result.document_id == 1
    assert result.valid_rows == 10
    assert result.invalid_rows == 0
    assert result.final_status == "PARTIAL_LOADED"