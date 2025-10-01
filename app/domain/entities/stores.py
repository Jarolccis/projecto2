"""Store domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Stores:
    id: Optional[int]
    business_unit_id: int
    store_id: int
    name: str
    zone_id: Optional[int]
    zone_name: Optional[str]
    channel_id: Optional[int]
    channel_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        business_unit_id: int,
        store_id: int,
        name: str,
        zone_id: Optional[int] = None,
        zone_name: Optional[str] = None,
        channel_id: Optional[int] = None,
        channel_name: Optional[str] = None,
        is_active: bool = True,
    ) -> "Stores":
        now = datetime.utcnow()
        return cls(
            id=None,  # Will be set by the database
            business_unit_id=business_unit_id,
            store_id=store_id,
            name=name,
            zone_id=zone_id,
            zone_name=zone_name,
            channel_id=channel_id,
            channel_name=channel_name,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: Optional[str] = None,
        zone_id: Optional[int] = None,
        zone_name: Optional[str] = None,
        channel_id: Optional[int] = None,
        channel_name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if zone_id is not None:
            self.zone_id = zone_id
        if zone_name is not None:
            self.zone_name = zone_name
        if channel_id is not None:
            self.channel_id = channel_id
        if channel_name is not None:
            self.channel_name = channel_name
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = datetime.utcnow()


