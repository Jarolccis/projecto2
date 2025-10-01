"""SQLAlchemy ORM model for lookup_value table."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.infrastructure.postgres.session import Base


class LookupValueModel(Base):
    """Lookup Value ORM model."""
    
    __tablename__ = 'lookup_value'
    __table_args__ = (
        UniqueConstraint('category_id', 'option_key', name='uq_category_optionkey'),
        UniqueConstraint('category_id', 'option_value', name='uq_category_optionvalue', deferrable=True),
        {'schema': 'tottus_pe'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('tottus_pe.lookup_category.id', ondelete='CASCADE'), nullable=False)
    option_key = Column(String(100), nullable=False)
    display_value = Column(String(255), nullable=False)
    option_value = Column(String(100), nullable=True)
    parent_id = Column(Integer, ForeignKey('tottus_pe.lookup_value.id', ondelete='CASCADE'), nullable=True)
    extra_data = Column('metadata', JSONB, nullable=True, default=lambda: {})
    sort_order = Column(SmallInteger, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
    
    # Relationships
    category = relationship("LookupCategoryModel", back_populates="values")
    parent = relationship("LookupValueModel", remote_side=[id], back_populates="children")
    children = relationship("LookupValueModel", back_populates="parent")
