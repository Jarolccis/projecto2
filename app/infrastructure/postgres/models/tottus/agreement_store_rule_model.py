"""Agreement Store Rule SQLAlchemy model."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func

from app.infrastructure.postgres.session import Base
from app.core.agreement_enums import StoreRuleStatusEnum


class AgreementStoreRuleModel(Base):
    """Agreement Store Rule database model."""
    
    __tablename__ = "agreement_store_rules"
    __table_args__ = {"schema": "tottus_pe"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    status = Column(ENUM(StoreRuleStatusEnum, name="store_rule_status_enum", schema="tottus_pe"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    created_by_user_email = Column(String(320), nullable=False)
    updated_status_by_user_email = Column(String(320), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
