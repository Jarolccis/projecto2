"""SQLAlchemy ORM model for lookup_category table."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.postgres.session import Base


class LookupCategoryModel(Base):
    """Lookup Category ORM model."""
    
    __tablename__ = 'lookup_category'
    __table_args__ = (
        UniqueConstraint('code', name='dropdown_category_code_key'),
        {'schema': 'tottus_pe'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    code = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    allow_hierarchy = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
    
    # Relationships
    values = relationship("LookupValueModel", back_populates="category")
