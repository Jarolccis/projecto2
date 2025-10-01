from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.infrastructure.postgres.session import Base


class BusinessUnits(Base):
    __tablename__ = 'business_units'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    code = Column(String(15), nullable=False)
    business_unit = Column(String(200), nullable=False)
    country = Column(String(60), nullable=False)
    country_iso_code = Column(String(15), nullable=False)
    tax_id = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
