import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.repositories.agreements_bulk_upload_repository import AgreementsBulkUploadRepository
from app.domain.entities.agreements_bulk_upload import AgreementsBulkUploadDocument, AgreementsBulkUploadDocumentRow
from uuid import uuid4

@pytest.mark.asyncio
def make_session_with_get(return_value):
    session = MagicMock()
    session.get = AsyncMock(return_value=return_value)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_create_document_success():
    session = MagicMock()
    repo = AgreementsBulkUploadRepository(session)
    doc = MagicMock(business_unit_id=1, status_id='1', full_path_document='path', comments=None, document_uid=uuid4(), source_system='SPF', created_by_user_email='test@example.com')
    with patch.object(session, 'add'), patch.object(session, 'flush', AsyncMock()), patch.object(session, 'refresh', AsyncMock()):
        with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._document_to_entity', return_value=doc):
            result = await repo.create_document(doc)
            assert result == doc

@pytest.mark.asyncio
async def test_create_document_db_error():
    session = MagicMock()
    repo = AgreementsBulkUploadRepository(session)
    doc = MagicMock()
    with patch.object(session, 'add', side_effect=Exception('db error')):
        with pytest.raises(Exception):
            await repo.create_document(doc)

@pytest.mark.asyncio
async def test_get_document_by_id_success():
    mock_model = MagicMock()
    mock_model.id = 1
    session = make_session_with_get(mock_model)
    repo = AgreementsBulkUploadRepository(session)
    with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._document_to_entity', return_value=mock_model):
        result = await repo.get_document_by_id(1)
        assert result.id == 1

@pytest.mark.asyncio
async def test_get_document_by_id_not_found():
    session = make_session_with_get(None)
    repo = AgreementsBulkUploadRepository(session)
    result = await repo.get_document_by_id(999)
    assert result is None

@pytest.mark.asyncio
async def test_create_document_rows_success():
    session = MagicMock()
    repo = AgreementsBulkUploadRepository(session)
    rows = [MagicMock() for _ in range(2)]
    with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._row_entity_to_dict', return_value={}):
        session.execute = AsyncMock()
        session.flush = AsyncMock()
        result = await repo.create_document_rows(rows)
        assert isinstance(result, list)

@pytest.mark.asyncio
async def test_update_document_status_success():
    mock_model = MagicMock(id=1)
    session = make_session_with_get(mock_model)
    session.commit = AsyncMock()
    repo = AgreementsBulkUploadRepository(session)
    with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._document_to_entity', return_value=mock_model):
        result = await repo.update_document_status(1, '1')
        assert result.id == 1

@pytest.mark.asyncio
async def test_validate_document_rows_success():
    session = MagicMock()
    session.flush = AsyncMock()
    repo = AgreementsBulkUploadRepository(session)
    # Simula el resultado esperado
    row = MagicMock(success=True, message="ok")
    result_mock = MagicMock()
    result_mock.fetchone = MagicMock(return_value=row)
    session.execute = AsyncMock(return_value=result_mock)
    result = await repo.validate_document_rows(1, valid_skus=['SKU1'])
    assert isinstance(result, tuple)

@pytest.mark.asyncio
async def test_resolve_document_rows_success():
    session = MagicMock()
    session.flush = AsyncMock()
    repo = AgreementsBulkUploadRepository(session)
    row = MagicMock(success=True, message="ok")
    result_mock = MagicMock()
    result_mock.fetchone = MagicMock(return_value=row)
    session.execute = AsyncMock(return_value=result_mock)
    result = await repo.resolve_document_rows(1, 'user@example.com')
    assert isinstance(result, tuple)

@pytest.mark.asyncio
async def test_create_agreements_from_resolved_rows_success():
    mock_model = MagicMock(business_unit_id=1, source_system='SPF')
    session = make_session_with_get(mock_model)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    repo = AgreementsBulkUploadRepository(session)
    
    # Crear mock de filas resueltas con datos más realistas
    mock_resolved_row = MagicMock()
    mock_resolved_row.id = 1
    mock_resolved_row.sku = "TEST_SKU"
    mock_resolved_row.start_date_parsed = "2023-01-01"
    mock_resolved_row.end_date_parsed = "2023-12-31"
    mock_resolved_row.rebate_type_id = 1
    mock_resolved_row.concept_id = 1
    mock_resolved_row.note = "Test note"
    mock_resolved_row.spf_code = "TEST_CODE"
    mock_resolved_row.spf_description = "Test description"
    mock_resolved_row.unit_rebate_num = 100.0
    mock_resolved_row.billing_type_id = 1
    mock_resolved_row.pmm_user_id = "test_user"
    mock_resolved_row.group_id = 1
    mock_resolved_row.excluded_flag_ids = None
    mock_resolved_row.included_store_ids = None
    mock_resolved_row.excluded_store_ids = None
    
    # Configurar el mock para que devuelva filas reales
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_resolved_row])))
    session.execute = AsyncMock(return_value=result_mock)
    
    # Mockear los modelos correctamente
    agreement_model = MagicMock()
    agreement_model.__table__ = MagicMock()
    
    # Mockear la inserción de agreements con resultado que incluya IDs
    mock_agreements_result = MagicMock()
    mock_agreements_result.fetchall = MagicMock(return_value=[(1001,)])  # Un ID de acuerdo simulado
    
    mock_insert = MagicMock()
    mock_insert.returning = MagicMock(return_value=mock_insert)
    agreement_model.__table__.insert = MagicMock(return_value=mock_insert)
    
    # Configurar session.execute para devolver diferentes resultados según la consulta
    def execute_side_effect(*args, **kwargs):
        # Si es la consulta de inserción de agreements, devolver mock_agreements_result
        if hasattr(args[0], 'returning') and args[0].returning is not None:
            return mock_agreements_result
        # Para otras consultas, usar el result_mock existente
        return result_mock
    
    session.execute.side_effect = execute_side_effect
    
    product_model = MagicMock()
    product_model.__table__ = MagicMock()
    product_model.__table__.insert = MagicMock(return_value=MagicMock())
    
    excluded_flag_model = MagicMock()
    excluded_flag_model.__table__ = MagicMock()
    excluded_flag_model.__table__.insert = MagicMock(return_value=MagicMock())
    
    store_rule_model = MagicMock()
    store_rule_model.__table__ = MagicMock()
    store_rule_model.__table__.insert = MagicMock(return_value=MagicMock())
    
    # Mock para Sku
    mock_sku = MagicMock()
    mock_sku.sku = "TEST_SKU"
    mock_sku.descripcion_sku = "Test SKU Description"
    mock_sku.codigo_division = "DIV01"
    mock_sku.division = "Division 01"
    mock_sku.codigo_departamento = "DEP01"
    mock_sku.departamento = "Departamento 01"
    mock_sku.codigo_subdepartamento = "SUBDEP01"
    mock_sku.subdepartamento = "Subdepartamento 01"
    mock_sku.codigo_clase = "CLS01"
    mock_sku.clase = "Clase 01"
    mock_sku.codigo_subclase = "SUBCLS01"
    mock_sku.subclase = "Subclase 01"
    mock_sku.marca_id = 1
    mock_sku.marca = "Test Brand"
    mock_sku.proveedor_id = 1
    mock_sku.proveedor = "Test Supplier"
    mock_sku.ruc_proveedor = "12345678901"
    
    with patch('app.infrastructure.repositories.agreements_bulk_upload_repository.AgreementModel', agreement_model):
        with patch('app.infrastructure.repositories.agreements_bulk_upload_repository.AgreementProductModel', product_model):
            with patch('app.infrastructure.repositories.agreements_bulk_upload_repository.AgreementExcludedFlagModel', excluded_flag_model):
                with patch('app.infrastructure.repositories.agreements_bulk_upload_repository.AgreementStoreRuleModel', store_rule_model):
                    result = await repo.create_agreements_from_resolved_rows(1, 'user@example.com', skus=[mock_sku])
                    assert isinstance(result, tuple)
                    assert result[0] is True  # success
                    assert "Successfully created" in result[1]  # message
                    assert result[2] == 1  # agreements_created

@pytest.mark.asyncio
async def test_get_document_with_rows_success():
    mock_model = MagicMock(id=1)
    session = make_session_with_get(mock_model)
    repo = AgreementsBulkUploadRepository(session)
    with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._document_to_entity', return_value=mock_model):
        with patch('app.infrastructure.repositories.agreements_bulk_upload_repository._row_to_entity', return_value=MagicMock()):
            result_mock = MagicMock()
            result_mock.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[MagicMock()])))
            session.execute = AsyncMock(return_value=result_mock)
            result = await repo.get_document_with_rows(1)
            assert isinstance(result, tuple)
