"""SQLAlchemy ORM models for Store."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from app.infrastructure.postgres.session import Base


class StoresModel(Base):
    """Store ORM model."""

    __tablename__ = "stores"
    __table_args__ = (
        UniqueConstraint('business_unit_id', 'store_id', name='stores_business_unit_store_unique'),
        {"schema": "tottus_pe"}
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_unit_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    zone_id = Column(Integer, nullable=True)
    zone_name = Column(String(255), nullable=True)
    channel_id = Column(Integer, nullable=True)
    channel_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

 