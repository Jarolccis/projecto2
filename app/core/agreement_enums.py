"""Agreement domain enums."""

from enum import Enum


class SourceSystemEnum(str, Enum):
    """Source system enumeration for agreements.
    
    Corresponds to PostgreSQL enum: tottus_pe.source_system_enum
    Values: 'SPF', 'PMM'
    """
    
    SPF = "SPF"
    PMM = "PMM"


class StoreRuleStatusEnum(str, Enum):
    """Store rule status enumeration for agreement store rules.
    
    Corresponds to PostgreSQL enum: tottus_pe.store_rule_status_enum
    Values: 'INCLUDE', 'EXCLUDE'
    """
    
    INCLUDE = "INCLUDE"
    EXCLUDE = "EXCLUDE"


class AgreementBulkUploadStatusEnum(str, Enum):
    """Agreement bulk upload status enumeration.
    
    Status codes for bulk upload document processing.
    """
    
    IN_PROGRESS = "1"
    PENDING = "2"
    UPLOADED = "3"
    PARTIAL_LOADED = "4"
    ERROR = "5"
    CANCELLED = "6"
    WAITING_APPROVAL = "7"


class AgreementStatusEnum(str, Enum):
    """Agreement status enumeration.
    
    Status codes for agreement states.
    """
    
    GENERATED = "1"
    APPROVED = "2"
    CANCELLED = "3"
    EXPIRED = "4"
    DRAFT = "5"
    REJECTED = "6"
    DELETED = "7"
