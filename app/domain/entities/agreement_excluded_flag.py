
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AgreementExcludedFlag:
    id: Optional[int]
    agreement_id: int
    excluded_flag_id: str
    active: bool
    created_at: datetime
    created_by_user_email: str
    updated_at: datetime
    updated_status_by_user_email: Optional[str]
    excluded_flag_name: Optional[str] = None

    @classmethod
    def create(
        cls,
        agreement_id: int,
        excluded_flag_id: str,
        created_by_user_email: str,
        active: bool = True,
    ) -> "AgreementExcludedFlag":
        now = datetime.utcnow()
        return cls(
            id=None,  
            agreement_id=agreement_id,
            excluded_flag_id=excluded_flag_id,
            active=active,
            created_at=now,
            created_by_user_email=created_by_user_email,
            updated_at=now,
            updated_status_by_user_email=None,
        )
