import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.interfaces.api.controllers.skus_controller import SkuController
from app.interfaces.schemas.sku_schema import SkuCodesRequest, SkuResponse

class DummyRequest:
    state = type("obj", (), {"user": type("User", (), {"bu_id": 1, "email": "test@example.com"})()})

@pytest.mark.asyncio
async def test_get_skus_success():
    controller = SkuController()
    request = DummyRequest()
    sku_codes = SkuCodesRequest(sku_codes=["SKU1", "SKU2"])
    use_cases = AsyncMock()
    dummy_sku = SkuResponse(
        sku="SKU1",
        descripcion_sku="desc",
        costo_reposicion=10.0,
        estado_id=1,
        marca_id=1,
        marca="marca",
        subclase_id=1,
        codigo_subclase="01",
        subclase="subclase",
        clase_id=1,
        codigo_clase="01",
        clase="clase",
        subdepartamento_id=1,
        codigo_subdepartamento="01",
        subdepartamento="subdep",
        departamento_id=1,
        codigo_departamento="01",
        departamento="dep",
        division_id=1,
        codigo_division="01",
        division="div",
        proveedor_id=1,
        ruc_proveedor="ruc",
        proveedor="prov"
    )
    dummy_sku2 = dummy_sku.copy(update={"sku": "SKU2"})
    use_cases.get_skus_by_codes.return_value = [dummy_sku, dummy_sku2]
    response = await controller.get_skus_by_codes(request, "SKU1,SKU2", use_cases)
    assert response.count == 2

@pytest.mark.asyncio
async def test_get_skus_error():
    controller = SkuController()
    request = DummyRequest()
    use_cases = AsyncMock()
    use_cases.get_skus_by_codes.side_effect = Exception("fail")
    with pytest.raises(HTTPException):
        await controller.get_skus_by_codes(request, "SKU1", use_cases)
