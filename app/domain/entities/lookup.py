from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class LookupCategory:
    id: int
    code: str
    name: str
    allow_hierarchy: bool
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass 
class LookupValue:
    id: int
    category_id: int
    option_key: str
    display_value: str
    option_value: Optional[str]
    parent_id: Optional[int]
    extra_data: Dict  # Maps to 'metadata' column in DB
    sort_order: int
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class LookupValueResult:
    lookup_value_id: int
    option_key: str
    display_value: str
    option_value: Optional[str]
    metadata: Dict
    sort_order: int
    parent_id: Optional[int]
