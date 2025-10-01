from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.infrastructure.postgres.session import Base


class Currencies(Base):
    __tablename__ = 'currencies'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(15), nullable=False)
    decimal_position = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
