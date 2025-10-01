"""Agreement SQLAlchemy model."""

from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func

from app.infrastructure.postgres.session import Base
from app.core.agreement_enums import SourceSystemEnum


class AgreementModel(Base):
    """Agreement database model."""
    
    __tablename__ = "agreements"
    __table_args__ = {"schema": "tottus_pe"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_unit_id = Column(Integer, nullable=False)
    agreement_number = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    agreement_type_id = Column(String(10), nullable=False)
    status_id = Column(String(10), nullable=False)
    rebate_type_id = Column(String(10), nullable=False)
    concept_id = Column(String(10), nullable=False)
    description = Column(String(70), nullable=True)
    activity_name = Column(String(100), nullable=True)
    source_system = Column(ENUM(SourceSystemEnum, name="source_system_enum", schema="tottus_pe"), nullable=False)
    spf_code = Column(String(50), nullable=True)
    spf_description = Column(String(100), nullable=True)
    currency_id = Column(Integer, nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    billing_type = Column(String(10), nullable=False)
    pmm_username = Column(String(10), nullable=True)
    store_grouping_id = Column(String(10), nullable=True)
    bulk_upload_document_id = Column(Integer, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    created_by_user_email = Column(String(320), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    updated_status_by_user_email = Column(String(320), nullable=True)
