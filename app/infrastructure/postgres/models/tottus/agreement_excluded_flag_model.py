"""Agreement Excluded Flag SQLAlchemy model."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.infrastructure.postgres.session import Base


class AgreementExcludedFlagModel(Base):
    """Agreement Excluded Flag database model."""
    
    __tablename__ = "agreement_excluded_flags"
    __table_args__ = {"schema": "tottus_pe"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer, nullable=False)
    excluded_flag_id = Column(String(10), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    created_by_user_email = Column(String(320), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    updated_status_by_user_email = Column(String(320), nullable=True)
