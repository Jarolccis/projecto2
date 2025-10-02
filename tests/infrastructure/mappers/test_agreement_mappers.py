import pytest
from unittest.mock import MagicMock
from app.infrastructure.mappers import agreement_mappers


from app.core.agreement_enums import SourceSystemEnum
from datetime import date
from decimal import Decimal
class DummyRow:
    def __init__(self):
        self.agreement_id = 1
        self.agreement_number = 1001
        self.agreement_description = "desc"
        self.description = "desc"
        self.source_system = SourceSystemEnum.SPF
        self.start_date = date(2023, 1, 1)
        self.end_date = date(2023, 12, 31)
        self.created_at = MagicMock(isoformat=lambda: "2023-01-01T00:00:00")
        self.created_by_user_email = "user@test.com"
        self.updated_at = MagicMock(isoformat=lambda: "2023-01-02T00:00:00")
        self.updated_status_by_user_email = "user2@test.com"
        self.status_id = "ACTIVE"
        self.status_description = "Activo"
        self.rebate_type_id = "REBATE"
        self.rebate_type_description = "Rebate Desc"
        self.concept_id = "C1"
        self.concept_description = "Concept Desc"
        self.spf_code = "SPF1"
        self.spf_description = "SPF Desc"
        self.currency_id = 1
        self.currency_code = "PEN"
        self.unit_price = Decimal("10.0")
        self.billing_type = "BILL"
        self.billing_type_description = "Bill Desc"
        self.pmm_username = "user"
        self.pmm_username_description = "User Desc"
        self.store_grouping_id = "SG1"
        self.store_grouping_description = "SG Desc"
        self.sku_code = "SKU1"
        self.sku_description = "SKU Desc"
        self.division_code = "D1"
        self.division_name = "Div Name"
        self.department_code = "DEP1"
        self.department_name = "Dep Name"
        self.subdepartment_code = "SUB1"
        self.subdepartment_name = "Sub Name"
        self.class_code = "CL1"
        self.class_name = "Class Name"
        self.subclass_code = "SCL1"
        self.subclass_name = "SubClass Name"
        self.brand_id = "B1"
        self.brand_name = "Brand Name"
        self.supplier_id = 123
        self.supplier_name = "Supplier Name"
        self.supplier_ruc = "RUC1"


def test_map_search_result_to_agreement_item_success():
    row = DummyRow()
    item = agreement_mappers.map_search_result_to_agreement_item(row)
    assert item.agreement_number == 1001
    assert item.status_id == "ACTIVE"


def test_map_search_result_to_agreement_item_missing_column():
    row = DummyRow()
    del row.status_id
    with pytest.raises(AttributeError):
        agreement_mappers.map_search_result_to_agreement_item(row)


def test_map_search_results_to_agreement_items():
    rows = [DummyRow(), DummyRow()]
    items = agreement_mappers.map_search_results_to_agreement_items(rows)
    assert len(items) == 2


def test_map_request_to_agreement_product_success():
    req = MagicMock()
    req.sku_code = "SKU1"
    req.sku_description = "desc"
    req.division_code = "D1"
    req.division_name = "Div Name"
    req.department_code = "DEP1"
    req.department_name = "Dep Name"
    req.subdepartment_code = "SUB1"
    req.subdepartment_name = "Sub Name"
    req.class_code = "CL1"
    req.class_name = "Class Name"
    req.subclass_code = "SCL1"
    req.subclass_name = "SubClass Name"
    req.brand_id = "B1"
    req.brand_name = "Brand Name"
    req.supplier_id = "SUP1"
    req.supplier_name = "Supplier Name"
    req.supplier_ruc = "RUC1"
    prod = agreement_mappers.map_request_to_agreement_product(req, 1)
    assert prod.agreement_id == 1
    assert prod.sku_code == "SKU1"


def test_map_request_to_agreement_product_error():
    req = object()  # No tiene atributos
    with pytest.raises(ValueError):
        agreement_mappers.map_request_to_agreement_product(req, 1)


def test_map_request_to_agreement_store_rule_success():
    req = MagicMock()
    req.store_id = "S1"
    req.status = "ACTIVE"
    rule = agreement_mappers.map_request_to_agreement_store_rule(req, 2)
    assert rule.agreement_id == 2
    assert rule.store_id == "S1"


def test_map_request_to_agreement_store_rule_error():
    req = object()
    with pytest.raises(ValueError):
        agreement_mappers.map_request_to_agreement_store_rule(req, 2)


def test_map_request_to_agreement_excluded_flag_success():
    req = MagicMock()
    req.excluded_flag_id = 5
    flag = agreement_mappers.map_request_to_agreement_excluded_flag(req, 3)
    assert flag.agreement_id == 3
    assert flag.excluded_flag_id == 5


def test_map_request_to_agreement_excluded_flag_error():
    req = object()
    with pytest.raises(ValueError):
        agreement_mappers.map_request_to_agreement_excluded_flag(req, 3)


def test_map_request_to_agreement_success():
    req = MagicMock()
    req.business_unit_id = 1
    req.agreement_type_id = "T1"
    req.status_id = "ACTIVE"
    req.rebate_type_id = "REBATE"
    req.concept_id = "C1"
    req.source_system = "SYS"
    req.unit_price = 10.0
    req.billing_type = "BILL"
    req.agreement_number = "A-001"
    req.start_date = "2023-01-01"
    req.end_date = "2023-12-31"
    req.description = "desc"
    req.activity_name = "act"
    req.spf_code = "SPF1"
    req.spf_description = "spfdesc"
    req.currency_id = "PEN"
    req.pmm_username = "user"
    req.store_grouping_id = "SG1"
    agreement = agreement_mappers.map_request_to_agreement(req)
    assert agreement.business_unit_id == 1
    assert agreement.agreement_type_id == "T1"


def test_map_request_to_agreement_error():
    req = object()
    with pytest.raises(ValueError):
        agreement_mappers.map_request_to_agreement(req)


def test_map_update_request_to_agreement_success():
    req = MagicMock()
    req.business_unit_id = 1
    req.agreement_type_id = "T1"
    req.status_id = "ACTIVE"
    req.rebate_type_id = "REBATE"
    req.concept_id = "C1"
    req.source_system = "SYS"
    req.unit_price = 10.0
    req.billing_type = "BILL"
    req.start_date = "2023-01-01"
    req.end_date = "2023-12-31"
    req.description = "desc"
    req.activity_name = "act"
    req.spf_code = "SPF1"
    req.spf_description = "spfdesc"
    req.currency_id = "PEN"
    req.pmm_username = "user"
    req.store_grouping_id = "SG1"
    agreement = agreement_mappers.map_update_request_to_agreement(req)
    assert agreement.business_unit_id == 1
    assert agreement.agreement_type_id == "T1"


def test_map_update_request_to_agreement_error():
    req = object()
    with pytest.raises(ValueError):
        agreement_mappers.map_update_request_to_agreement(req)


def test_map_requests_to_agreement_products():
    req = MagicMock()
    req.sku_code = "SKU1"
    req.sku_description = "desc"
    req.division_code = "D1"
    req.division_name = "Div Name"
    req.department_code = "DEP1"
    req.department_name = "Dep Name"
    req.subdepartment_code = "SUB1"
    req.subdepartment_name = "Sub Name"
    req.class_code = "CL1"
    req.class_name = "Class Name"
    req.subclass_code = "SCL1"
    req.subclass_name = "SubClass Name"
    req.brand_id = "B1"
    req.brand_name = "Brand Name"
    req.supplier_id = "SUP1"
    req.supplier_name = "Supplier Name"
    req.supplier_ruc = "RUC1"
    products = agreement_mappers.map_requests_to_agreement_products([req, req], 1)
    assert len(products) == 2


def test_map_requests_to_agreement_store_rules():
    req = MagicMock()
    req.store_id = "S1"
    req.status = "ACTIVE"
    rules = agreement_mappers.map_requests_to_agreement_store_rules([req, req], 2)
    assert len(rules) == 2


def test_map_requests_to_agreement_excluded_flags():
    req = MagicMock()
    req.excluded_flag_id = 5
    flags = agreement_mappers.map_requests_to_agreement_excluded_flags([req, req], 3)
    assert len(flags) == 2
