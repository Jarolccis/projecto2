from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.core.agreement_enums import SourceSystemEnum


@dataclass
class Agreement:
    id: Optional[int]
    business_unit_id: int
    agreement_number: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]
    agreement_type_id: Optional[str]
    status_id: str
    rebate_type_id: str
    concept_id: str
    description: Optional[str]
    activity_name: Optional[str]
    source_system: SourceSystemEnum
    spf_code: Optional[str]
    spf_description: Optional[str]
    currency_id: Optional[int]
    unit_price: Decimal
    billing_type: str
    pmm_username: Optional[str]
    store_grouping_id: Optional[str]
    bulk_upload_document_id: Optional[int]
    active: bool
    created_at: datetime
    created_by_user_email: str
    updated_at: datetime
    updated_status_by_user_email: Optional[str]
    
    # Additional fields with lookup value descriptions
    status_description: Optional[str] = None
    rebate_type_description: Optional[str] = None
    concept_description: Optional[str] = None
    billing_type_description: Optional[str] = None
    pmm_username_description: Optional[str] = None
    store_grouping_description: Optional[str] = None

    @classmethod
    def create(
        cls,
        business_unit_id: int,
        agreement_type_id: Optional[str],
        status_id: str,
        rebate_type_id: str,
        concept_id: str,
        source_system: SourceSystemEnum,
        unit_price: Decimal,
        billing_type: str,
        created_by_user_email: str,
        agreement_number: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        description: Optional[str] = None,
        activity_name: Optional[str] = None,
        spf_code: Optional[str] = None,
        spf_description: Optional[str] = None,
        currency_id: Optional[int] = None,
        pmm_username: Optional[str] = None,
        store_grouping_id: Optional[str] = None,
        bulk_upload_document_id: Optional[int] = None,
        active: bool = True,
    ) -> "Agreement":
        now = datetime.utcnow()
        return cls(
            id=None,  
            business_unit_id=business_unit_id,
            agreement_number=agreement_number,
            start_date=start_date,
            end_date=end_date,
            agreement_type_id=agreement_type_id,
            status_id=status_id,
            rebate_type_id=rebate_type_id,
            concept_id=concept_id,
            description=description,
            activity_name=activity_name,
            source_system=source_system,
            spf_code=spf_code,
            spf_description=spf_description,
            currency_id=currency_id,
            unit_price=unit_price,
            billing_type=billing_type,
            pmm_username=pmm_username,
            store_grouping_id=store_grouping_id,
            bulk_upload_document_id=bulk_upload_document_id,
            active=active,
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_at=now,
            updated_status_by_user_email=None,
            # Los campos de descripción se inicializan como None
            status_description=None,
            rebate_type_description=None,
            concept_description=None,
            billing_type_description=None,
            pmm_username_description=None,
            store_grouping_description=None
        )
