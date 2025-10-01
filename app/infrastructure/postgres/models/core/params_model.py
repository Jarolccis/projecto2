from sqlalchemy import Boolean, Column, DateTime, Integer, Text

from app.infrastructure.postgres.session import Base


class Params(Base):
    __tablename__ = 'params'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    value = Column(Text, nullable=True)
    time_limit = Column(Integer, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
