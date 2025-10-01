from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, BigInteger, ForeignKey, Date, Numeric, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.infrastructure.postgres.session import Base


class AgreementsBulkUploadDocumentRowsModel(Base):
    """Model for agreements bulk upload document rows table."""
    
    __tablename__ = 'agreements_bulk_upload_document_rows'
    __table_args__ = {'schema': 'tottus_pe'}

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    bulk_document_id = Column(Integer, ForeignKey('tottus_pe.agreements_bulk_upload_documents.id', ondelete='CASCADE'), nullable=False)
    pmm_user = Column(String(255), nullable=True)
    group_name = Column(String(255), nullable=True)
    excluded_flags = Column(String(255), nullable=True)
    included_stores = Column(Text, nullable=True)
    excluded_stores = Column(Text, nullable=True)
    rebate_type = Column(String(255), nullable=True)
    concept = Column(String(255), nullable=True)
    note = Column(String(255), nullable=True)
    spf_code = Column(String(255), nullable=True)
    spf_description = Column(String(255), nullable=True)
    sku = Column(String(255), nullable=True)
    start_date = Column(String(255), nullable=True)
    end_date = Column(String(255), nullable=True)
    unit_rebate_pen = Column(String(255), nullable=True)
    billing_type = Column(String(255), nullable=True)
    observations = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by_user_email = Column(String(255), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Resolved fields
    pmm_user_id = Column(String(10), nullable=True)
    group_id = Column(String(10), nullable=True)
    rebate_type_id = Column(String(10), nullable=True)
    concept_id = Column(String(10), nullable=True)
    billing_type_id = Column(String(10), nullable=True)
    included_store_ids = Column(ARRAY(Integer), nullable=True)
    excluded_store_ids = Column(ARRAY(Integer), nullable=True)
    excluded_flag_ids = Column(ARRAY(Text), nullable=True)
    start_date_parsed = Column(Date, nullable=True)
    end_date_parsed = Column(Date, nullable=True)
    unit_rebate_num = Column(Numeric(12, 2), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(320), nullable=True)

    # Relationship to the parent document
    bulk_document = relationship("AgreementsBulkUploadDocumentsModel", back_populates="document_rows")
