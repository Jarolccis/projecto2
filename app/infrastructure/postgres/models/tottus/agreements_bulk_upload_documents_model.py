from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.infrastructure.postgres.session import Base
from app.core.agreement_enums import SourceSystemEnum


class AgreementsBulkUploadDocumentsModel(Base):
    """Model for agreements bulk upload documents table."""
    
    __tablename__ = 'agreements_bulk_upload_documents'
    __table_args__ = {'schema': 'tottus_pe'}

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    business_unit_id = Column(Integer, nullable=False)
    status_id = Column(String(10), nullable=False)
    full_path_document = Column(String, nullable=True)
    comments = Column(Text, nullable=True)
    document_uid = Column(UUID(as_uuid=True), nullable=False, unique=True)
    source_system = Column(Enum(SourceSystemEnum, name='source_system_enum', schema='tottus_pe'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by_user_email = Column(String(320), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship to document rows
    document_rows = relationship("AgreementsBulkUploadDocumentRowsModel", back_populates="bulk_document", cascade="all, delete-orphan")
