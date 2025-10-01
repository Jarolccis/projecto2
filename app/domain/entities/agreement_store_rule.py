from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.core.agreement_enums import StoreRuleStatusEnum


@dataclass
class AgreementStoreRule:
    id: Optional[int]
    agreement_id: int
    store_id: int
    status: StoreRuleStatusEnum
    active: bool
    created_at: datetime
    created_by_user_email: str
    updated_status_by_user_email: Optional[str]
    updated_at: datetime
    store_name: Optional[str] = None  # Store name from LEFT JOIN

    @classmethod
    def create(
        cls,
        agreement_id: int,
        store_id: int,
        status: StoreRuleStatusEnum,
        created_by_user_email: str,
        active: bool = True,
    ) -> "AgreementStoreRule":
        now = datetime.utcnow()
        return cls(
            id=None,  
            agreement_id=agreement_id,
            store_id=store_id,
            status=status,
            active=active,
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_status_by_user_email=None,
            updated_at=now,
        )
