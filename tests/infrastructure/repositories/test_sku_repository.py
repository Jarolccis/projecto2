import pytest
from unittest.mock import AsyncMock, MagicMock, create_autospec, patch
from app.infrastructure.repositories.sku_repository import SkuRepository
from google.api_core import exceptions as google_exceptions
from google.cloud.exceptions import NotFound, Forbidden
from app.domain.entities.sku import Sku

import types

@pytest.fixture(autouse=True)
def patch_bigquery_loader_and_helper():
    with patch("app.infrastructure.repositories.sku_repository.BigQueryLoader", return_value=MagicMock()):
        with patch("app.infrastructure.repositories.sku_repository.BigQueryHelper", return_value=MagicMock()):
            yield

@pytest.mark.asyncio
async def test_get_skus_success():
    repo = create_autospec(SkuRepository, instance=True)
    repo.get_skus_by_codes = AsyncMock(return_value=[MagicMock(sku_code="SKU1"), MagicMock(sku_code="SKU2")])
    result = await repo.get_skus_by_codes(["SKU1", "SKU2"])
    assert [r.sku_code for r in result] == ["SKU1", "SKU2"]

@pytest.mark.asyncio
async def test_get_skus_error():
    repo = create_autospec(SkuRepository, instance=True)
    repo.get_skus_by_codes = AsyncMock(side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await repo.get_skus_by_codes(["SKU1"])

@pytest.mark.asyncio
async def test_get_skus_by_codes_success(monkeypatch):
    repo = SkuRepository()
    repo.query_loader = MagicMock()
    repo.bigquery_helper = MagicMock()
    repo.query_loader.load_query.return_value = "SELECT * FROM skus"
    repo.bigquery_helper.execute_query.return_value = []
    # Simula el mapeo de resultados como lo espera el mapper real
    class Row:
        def __init__(self, sku):
            self.Sku = sku
            self.DescripcionSku = "desc"
            self.CostoReposicion = 0
            self.EstadoId = 0
            self.MarcaId = 0
            self.Marca = ""
            self.SubClaseId = 0
            self.CodigoSubClase = ""
            self.SubClase = ""
            self.ClaseId = 0
            self.CodigoClase = ""
            self.Clase = ""
            self.SubDepartamentoId = 0
            self.CodigoSubDepartamento = ""
            self.SubDepartamento = ""
            self.DepartamentoId = 0
            self.CodigoDepartamento = ""
            self.Departamento = ""
            self.DivisionId = 0
            self.CodigoDivision = ""
            self.Division = ""
            self.ProveedorId = 0
            self.RucProveedor = ""
            self.Proveedor = ""
    rows = [Row("SKU1"), Row("SKU2")]
    repo.bigquery_helper.execute_query.return_value = rows
    with pytest.MonkeyPatch.context() as m:
        from app.infrastructure.mappers import sku_mappers
        m.setattr(sku_mappers, "map_bigquery_results_to_skus", lambda results, _: [Sku.create(
            sku=row.Sku,
            descripcion_sku=row.DescripcionSku,
            costo_reposicion=row.CostoReposicion,
            estado_id=row.EstadoId,
            marca_id=row.MarcaId,
            marca=row.Marca,
            subclase_id=row.SubClaseId,
            codigo_subclase=row.CodigoSubClase,
            subclase=row.SubClase,
            clase_id=row.ClaseId,
            codigo_clase=row.CodigoClase,
            clase=row.Clase,
            subdepartamento_id=row.SubDepartamentoId,
            codigo_subdepartamento=row.CodigoSubDepartamento,
            subdepartamento=row.SubDepartamento,
            departamento_id=row.DepartamentoId,
            codigo_departamento=row.CodigoDepartamento,
            departamento=row.Departamento,
            division_id=row.DivisionId,
            codigo_division=row.CodigoDivision,
            division=row.Division,
            proveedor_id=row.ProveedorId,
            ruc_proveedor=row.RucProveedor,
            proveedor=row.Proveedor
        ) for row in results])
        result = await repo.get_skus_by_codes(["SKU1", "SKU2"])
        assert [r.sku for r in result] == ["SKU1", "SKU2"]

@pytest.mark.asyncio
async def test_get_skus_by_codes_deadline(monkeypatch):
    repo = SkuRepository()
    repo.query_loader = MagicMock()
    repo.bigquery_helper = MagicMock()
    repo.query_loader.load_query.return_value = "SELECT * FROM skus"
    repo.bigquery_helper.execute_query.side_effect = google_exceptions.DeadlineExceeded("timeout")
    with pytest.raises(Exception) as excinfo:
        await repo.get_skus_by_codes(["SKU1"])
    assert "excedió el límite de tiempo" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_skus_by_codes_forbidden(monkeypatch):
    repo = SkuRepository()
    repo.query_loader = MagicMock()
    repo.bigquery_helper = MagicMock()
    repo.query_loader.load_query.return_value = "SELECT * FROM skus"
    repo.bigquery_helper.execute_query.side_effect = Forbidden("forbidden")
    with pytest.raises(Exception) as excinfo:
        await repo.get_skus_by_codes(["SKU1"])
    assert "Sin permisos" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_skus_by_codes_notfound(monkeypatch):
    repo = SkuRepository()
    repo.query_loader = MagicMock()
    repo.bigquery_helper = MagicMock()
    repo.query_loader.load_query.return_value = "SELECT * FROM skus"
    repo.bigquery_helper.execute_query.side_effect = NotFound("not found")
    with pytest.raises(Exception) as excinfo:
        await repo.get_skus_by_codes(["SKU1"])
    assert "no encontrado" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_skus_by_codes_generic_exception(monkeypatch):
    repo = SkuRepository()
    repo.query_loader = MagicMock()
    repo.bigquery_helper = MagicMock()
    repo.query_loader.load_query.return_value = "SELECT * FROM skus"
    repo.bigquery_helper.execute_query.side_effect = Exception("fail")
    result = await repo.get_skus_by_codes(["SKU1"])
    assert result == []


def test_close_logs_and_closes_helper():
    repo = SkuRepository()
    repo.bigquery_helper = MagicMock()
    repo.close()
    repo.bigquery_helper.close.assert_called_once()
