from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.infrastructure.postgres.session import Base


class ModuleUsersModel(Base):
    __tablename__ = 'module_users'
    __table_args__ = {'schema': 'tottus_pe'}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_email = Column(String(320), nullable=False)
    module_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default='now()')
    updated_at = Column(DateTime, nullable=False, server_default='now()')
