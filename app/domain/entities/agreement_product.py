from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AgreementProduct:
    id: Optional[int]
    agreement_id: int
    sku_code: str
    sku_description: Optional[str]
    division_code: Optional[str]
    division_name: Optional[str]
    department_code: Optional[str]
    department_name: Optional[str]
    subdepartment_code: Optional[str]
    subdepartment_name: Optional[str]
    class_code: Optional[str]
    class_name: Optional[str]
    subclass_code: Optional[str]
    subclass_name: Optional[str]
    brand_id: Optional[str]
    brand_name: Optional[str]
    supplier_id: Optional[int]
    supplier_name: Optional[str]
    supplier_ruc: Optional[str]
    active: bool
    created_at: datetime
    created_by_user_email: str
    updated_status_by_user_email: Optional[str]
    updated_at: datetime

    @classmethod
    def create(
        cls,
        agreement_id: int,
        sku_code: str,
        created_by_user_email: str,
        sku_description: Optional[str] = None,
        division_code: Optional[str] = None,
        division_name: Optional[str] = None,
        department_code: Optional[str] = None,
        department_name: Optional[str] = None,
        subdepartment_code: Optional[str] = None,
        subdepartment_name: Optional[str] = None,
        class_code: Optional[str] = None,
        class_name: Optional[str] = None,
        subclass_code: Optional[str] = None,
        subclass_name: Optional[str] = None,
        brand_id: Optional[str] = None,
        brand_name: Optional[str] = None,
        supplier_id: Optional[int] = None,
        supplier_name: Optional[str] = None,
        supplier_ruc: Optional[str] = None,
        active: bool = True,
    ) -> "AgreementProduct":
        now = datetime.utcnow()
        return cls(
            id=None, 
            agreement_id=agreement_id,
            sku_code=sku_code,
            sku_description=sku_description,
            division_code=division_code,
            division_name=division_name,
            department_code=department_code,
            department_name=department_name,
            subdepartment_code=subdepartment_code,
            subdepartment_name=subdepartment_name,
            class_code=class_code,
            class_name=class_name,
            subclass_code=subclass_code,
            subclass_name=subclass_name,
            brand_id=brand_id,
            brand_name=brand_name,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            supplier_ruc=supplier_ruc,
            active=active,
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_status_by_user_email=None,
            updated_at=now,
        )
