from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.infrastructure.postgres.session import Base


class ModulesModel(Base):
    __tablename__ = 'modules'
    __table_args__ = {'schema': 'tottus_pe'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    business_unit_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(250), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
