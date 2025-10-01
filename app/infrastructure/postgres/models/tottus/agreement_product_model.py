"""Agreement Product SQLAlchemy model."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func

from app.infrastructure.postgres.session import Base


class AgreementProductModel(Base):
    """Agreement Product database model."""
    
    __tablename__ = "agreement_products"
    __table_args__ = {"schema": "tottus_pe"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer, nullable=False)
    sku_code = Column(String(50), nullable=False)
    sku_description = Column(String(255), nullable=True)
    division_code = Column(String(20), nullable=True)
    division_name = Column(String(120), nullable=True)
    department_code = Column(String(20), nullable=True)
    department_name = Column(String(120), nullable=True)
    subdepartment_code = Column(String(20), nullable=True)
    subdepartment_name = Column(String(120), nullable=True)
    class_code = Column(String(20), nullable=True)
    class_name = Column(String(120), nullable=True)
    subclass_code = Column(String(20), nullable=True)
    subclass_name = Column(String(120), nullable=True)
    brand_id = Column(String(80), nullable=True)
    brand_name = Column(String(120), nullable=True)
    supplier_id = Column(Integer, nullable=True)
    supplier_name = Column(String(160), nullable=True)
    supplier_ruc = Column(String(20), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    created_by_user_email = Column(String(320), nullable=False)
    updated_status_by_user_email = Column(String(320), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
