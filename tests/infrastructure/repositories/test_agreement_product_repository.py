import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.infrastructure.repositories.agreement_product_repository import PostgresAgreementProductRepository
from app.domain.entities.agreement_product import AgreementProduct

@pytest.mark.asyncio
async def test_create_agreement_product_success():
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    repo = PostgresAgreementProductRepository(session)
    entity = AgreementProduct(
        id=None,
        agreement_id=1,
        sku_code="SKU1",
        sku_description="desc",
        division_code="D1",
        division_name="Division",
        department_code="DEP1",
        department_name="Dept",
        subdepartment_code="SUB1",
        subdepartment_name="SubDept",
        class_code="C1",
        class_name="Class",
        subclass_code="SC1",
        subclass_name="SubClass",
        brand_id="B1",
        brand_name="Brand",
        supplier_id="S1",
        supplier_name="Supplier",
        supplier_ruc="RUC",
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at=None
    )
    mock_model = MagicMock(id=10, created_at="2024-01-01", updated_at="2024-01-02")
    with patch("app.infrastructure.repositories.agreement_product_repository.AgreementProductModel", return_value=mock_model):
        result = await repo.create_agreement_product(entity)
        assert result.id == 10
        assert result.created_at == "2024-01-01"
        assert result.updated_at == "2024-01-02"

@pytest.mark.asyncio
async def test_create_agreement_product_exception():
    session = MagicMock()
    session.flush = AsyncMock(side_effect=Exception("db error"))
    session.refresh = AsyncMock()
    repo = PostgresAgreementProductRepository(session)
    entity = AgreementProduct(
        id=None,
        agreement_id=1,
        sku_code="SKU1",
        sku_description="desc",
        division_code="D1",
        division_name="Division",
        department_code="DEP1",
        department_name="Dept",
        subdepartment_code="SUB1",
        subdepartment_name="SubDept",
        class_code="C1",
        class_name="Class",
        subclass_code="SC1",
        subclass_name="SubClass",
        brand_id="B1",
        brand_name="Brand",
        supplier_id="S1",
        supplier_name="Supplier",
        supplier_ruc="RUC",
        active=True,
        created_at=None,
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at=None
    )
    with patch("app.infrastructure.repositories.agreement_product_repository.AgreementProductModel"):
        with pytest.raises(Exception):
            await repo.create_agreement_product(entity)

@pytest.mark.asyncio
async def test_get_agreement_products_success():
    session = MagicMock()
    repo = PostgresAgreementProductRepository(session)
    model = MagicMock(
        id=1,
        agreement_id=1,
        sku_code="SKU1",
        sku_description="desc",
        division_code="D1",
        division_name="Division",
        department_code="DEP1",
        department_name="Dept",
        subdepartment_code="SUB1",
        subdepartment_name="SubDept",
        class_code="C1",
        class_name="Class",
        subclass_code="SC1",
        subclass_name="SubClass",
        brand_id="B1",
        brand_name="Brand",
        supplier_id="S1",
        supplier_name="Supplier",
        supplier_ruc="RUC",
        active=True,
        created_at="2024-01-01",
        created_by_user_email="user@example.com",
        updated_status_by_user_email="user@example.com",
        updated_at="2024-01-02"
    )
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[model])))
    session.execute = AsyncMock(return_value=result_mock)
    products = await repo.get_agreement_products(1)
    assert len(products) == 1
    assert products[0].sku_code == "SKU1"

@pytest.mark.asyncio
async def test_get_agreement_products_exception():
    session = MagicMock()
    session.execute = AsyncMock(side_effect=Exception("fail"))
    repo = PostgresAgreementProductRepository(session)
    with pytest.raises(Exception):
        await repo.get_agreement_products(1)

@pytest.mark.asyncio
async def test_exists_agreement_product_true():
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=1)
    session.execute = AsyncMock(return_value=result_mock)
    repo = PostgresAgreementProductRepository(session)
    exists = await repo.exists_agreement_product(1, "SKU1")
    assert exists is True

@pytest.mark.asyncio
async def test_exists_agreement_product_false():
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    session.execute = AsyncMock(return_value=result_mock)
    repo = PostgresAgreementProductRepository(session)
    exists = await repo.exists_agreement_product(1, "SKU1")
    assert exists is False

@pytest.mark.asyncio
async def test_exists_agreement_product_exception():
    session = MagicMock()
    session.execute = AsyncMock(side_effect=Exception("fail"))
    repo = PostgresAgreementProductRepository(session)
    with pytest.raises(Exception):
        await repo.exists_agreement_product(1, "SKU1")
