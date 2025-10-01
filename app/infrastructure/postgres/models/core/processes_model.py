from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.infrastructure.postgres.session import Base


class Processes(Base):
    __tablename__ = 'processes'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    business_unit_code = Column(String(15), nullable=False)
    country_iso_code = Column(String(15), nullable=False)
    name = Column(String(250), nullable=False)
    description = Column(String(500), nullable=True)
    url_api = Column(String(250), nullable=True)
    status = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_execution = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
