"""PostgreSQL agreements bulk upload repository implementation."""

from typing import List, Optional, Tuple, Dict
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.core_enums import CurrencyEnum
from app.core.agreement_enums import SourceSystemEnum
from app.domain.entities.agreements_bulk_upload import (
    AgreementsBulkUploadDocument,
    AgreementsBulkUploadDocumentRow
)
from app.domain.entities.sku import Sku
from app.domain.repositories.agreements_bulk_upload_repository import AgreementsBulkUploadRepository
from app.core.logging import LoggerMixin
from app.infrastructure.postgres.models.tottus.agreements_bulk_upload_documents_model import AgreementsBulkUploadDocumentsModel
from app.infrastructure.postgres.models.tottus.agreements_bulk_upload_document_rows_model import AgreementsBulkUploadDocumentRowsModel
from app.infrastructure.postgres.models.tottus.agreement_model import AgreementModel
from app.infrastructure.postgres.models.tottus.agreement_product_model import AgreementProductModel
from app.infrastructure.postgres.models.tottus.agreement_store_rule_model import AgreementStoreRuleModel
from app.infrastructure.postgres.models.tottus.agreement_excluded_flag_model import AgreementExcludedFlagModel
from app.core.agreement_enums import StoreRuleStatusEnum, AgreementStatusEnum


def _document_to_entity(model: AgreementsBulkUploadDocumentsModel) -> AgreementsBulkUploadDocument:
    """Convert Document ORM to Document entity."""
    return AgreementsBulkUploadDocument(
        id=model.id,
        business_unit_id=model.business_unit_id,
        status_id=model.status_id,
        full_path_document=model.full_path_document,
        comments=model.comments,
        document_uid=model.document_uid,
        source_system=model.source_system,
        created_at=model.created_at,
        created_by_user_email=model.created_by_user_email,
        updated_at=model.updated_at,
    )


def _row_entity_to_dict(row: AgreementsBulkUploadDocumentRow) -> dict:
    """Convert AgreementsBulkUploadDocumentRow entity to dict for bulk insert."""
    return {
        'bulk_document_id': row.bulk_document_id,
        'pmm_user': row.pmm_user,
        'group_name': row.group_name,
        'excluded_flags': row.excluded_flags,
        'included_stores': row.included_stores,
        'excluded_stores': row.excluded_stores,
        'rebate_type': row.rebate_type,
        'concept': row.concept,
        'note': row.note,
        'spf_code': row.spf_code,
        'spf_description': row.spf_description,
        'sku': row.sku,
        'start_date': row.start_date,
        'end_date': row.end_date,
        'unit_rebate_pen': row.unit_rebate_pen,
        'billing_type': row.billing_type,
        'observations': row.observations,
        'active': row.active,
        'created_by_user_email': row.created_by_user_email,
        'created_at': row.created_at,
        'updated_at': row.updated_at,
        
        # Resolved fields
        'pmm_user_id': row.pmm_user_id,
        'group_id': row.group_id,
        'rebate_type_id': row.rebate_type_id,
        'concept_id': row.concept_id,
        'billing_type_id': row.billing_type_id,
        'included_store_ids': row.included_store_ids,
        'excluded_store_ids': row.excluded_store_ids,
        'excluded_flag_ids': row.excluded_flag_ids,
        'start_date_parsed': row.start_date_parsed,
        'end_date_parsed': row.end_date_parsed,
        'unit_rebate_num': row.unit_rebate_num,
        'resolved_at': row.resolved_at,
        'resolved_by': row.resolved_by,
    }


def _row_to_entity(model: AgreementsBulkUploadDocumentRowsModel) -> AgreementsBulkUploadDocumentRow:
    """Convert Row ORM to Row entity."""
    return AgreementsBulkUploadDocumentRow(
        id=model.id,
        bulk_document_id=model.bulk_document_id,
        pmm_user=model.pmm_user,
        group_name=model.group_name,
        excluded_flags=model.excluded_flags,
        included_stores=model.included_stores,
        excluded_stores=model.excluded_stores,
        rebate_type=model.rebate_type,
        concept=model.concept,
        note=model.note,
        spf_code=model.spf_code,
        spf_description=model.spf_description,
        sku=model.sku,
        start_date=model.start_date,
        end_date=model.end_date,
        unit_rebate_pen=model.unit_rebate_pen,
        billing_type=model.billing_type,
        observations=model.observations,
        active=model.active,
        created_at=model.created_at,
        created_by_user_email=model.created_by_user_email,
        updated_at=model.updated_at,
        
        # New resolved fields
        pmm_user_id=model.pmm_user_id,
        group_id=model.group_id,
        rebate_type_id=model.rebate_type_id,
        concept_id=model.concept_id,
        billing_type_id=model.billing_type_id,
        included_store_ids=model.included_store_ids,
        excluded_store_ids=model.excluded_store_ids,
        excluded_flag_ids=model.excluded_flag_ids,
        start_date_parsed=model.start_date_parsed,
        end_date_parsed=model.end_date_parsed,
        unit_rebate_num=model.unit_rebate_num,
        resolved_at=model.resolved_at,
        resolved_by=model.resolved_by,
    )


class AgreementsBulkUploadRepository(AgreementsBulkUploadRepository, LoggerMixin):
    """PostgreSQL implementation of AgreementsBulkUploadRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an async session."""
        self._session = session

    async def create_document(self, document: AgreementsBulkUploadDocument) -> AgreementsBulkUploadDocument:
        """Create a new bulk upload document."""
        try:
            model = AgreementsBulkUploadDocumentsModel(
                business_unit_id=document.business_unit_id,
                status_id=document.status_id,
                full_path_document=document.full_path_document,
                comments=document.comments,
                document_uid=document.document_uid,
                source_system=document.source_system,
                created_by_user_email=document.created_by_user_email
            )
            
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            
            self.log_info("Bulk upload document created successfully", document_id=model.id)
            return _document_to_entity(model)
        except SQLAlchemyError as e:
            self.log_error("Database error creating document", error=str(e))
            raise Exception(f"Error creating document: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error creating document", error=str(e))
            raise Exception(f"Unexpected error creating document: {str(e)}")

    async def get_document_by_id(self, document_id: int) -> Optional[AgreementsBulkUploadDocument]:
        """Get document by ID."""
        try:
            model = await self._session.get(AgreementsBulkUploadDocumentsModel, document_id)
            if model is None:
                self.log_info("Bulk upload document not found by ID", document_id=document_id)
                return None
            
            self.log_info("Bulk upload document retrieved by ID", document_id=document_id)
            return _document_to_entity(model)
        except SQLAlchemyError as e:
            self.log_error("Database error getting document by ID", error=str(e), document_id=document_id)
            raise Exception(f"Error getting document by ID: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error getting document by ID", error=str(e), document_id=document_id)
            raise Exception(f"Unexpected error getting document by ID: {str(e)}")

    async def get_document_by_uid(self, document_uid: UUID) -> Optional[AgreementsBulkUploadDocument]:
        """Get document by UID."""
        try:
            stmt = select(AgreementsBulkUploadDocumentsModel).where(
                AgreementsBulkUploadDocumentsModel.document_uid == document_uid
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model is None:
                self.log_info("Bulk upload document not found by UID", document_uid=str(document_uid))
                return None
            
            self.log_info("Bulk upload document retrieved by UID", document_uid=str(document_uid))
            return _document_to_entity(model)
        except SQLAlchemyError as e:
            self.log_error("Database error getting document by UID", error=str(e), document_uid=str(document_uid))
            raise Exception(f"Error getting document by UID: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error getting document by UID", error=str(e), document_uid=str(document_uid))
            raise Exception(f"Unexpected error getting document by UID: {str(e)}")

    async def create_document_rows(self, rows: List[AgreementsBulkUploadDocumentRow]) -> List[AgreementsBulkUploadDocumentRow]:
        """Create multiple document rows using optimized bulk insert for better performance."""
        try:
            # Convert domain entities to dicts using helper function
            rows_data = [_row_entity_to_dict(row) for row in rows]
            
            # Optimized bulk insert - 5-10x faster than add_all + individual refresh
            await self._session.execute(
                AgreementsBulkUploadDocumentRowsModel.__table__.insert(),
                rows_data
            )
            await self._session.flush()
            
            self.log_info("Bulk upload document rows created successfully using optimized bulk insert", 
                         total_rows=len(rows_data),
                         performance_mode="bulk_insert_optimized")
            
            # Return original entities (IDs won't be available, but it's much faster)
            # For 1k+ rows this is 5-10x faster than implementation with individual refresh
            return rows
        except SQLAlchemyError as e:
            self.log_error("Database error creating document rows", error=str(e))
            raise Exception(f"Error creating document rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error creating document rows", error=str(e))
            raise Exception(f"Unexpected error creating document rows: {str(e)}")

    async def get_document_rows(self, document_id: int) -> List[AgreementsBulkUploadDocumentRow]:
        """Get all rows for a document."""
        try:
            stmt = select(AgreementsBulkUploadDocumentRowsModel).where(
                AgreementsBulkUploadDocumentRowsModel.bulk_document_id == document_id
            ).order_by(AgreementsBulkUploadDocumentRowsModel.id)
            
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            
            self.log_info("Document rows retrieved successfully", 
                         document_id=document_id, 
                         total_rows=len(models))
            
            return [_row_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            self.log_error("Database error getting document rows", error=str(e), document_id=document_id)
            raise Exception(f"Error getting document rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error getting document rows", error=str(e), document_id=document_id)
            raise Exception(f"Unexpected error getting document rows: {str(e)}")

    async def update_document_status(self, document_id: int, status_id: str, comments: Optional[str] = None) -> Optional[AgreementsBulkUploadDocument]:
        """Update document status and optionally comments."""
        try:
            model = await self._session.get(AgreementsBulkUploadDocumentsModel, document_id)
            if model is None:
                self.log_warning("Document not found for status update", document_id=document_id)
                return None
            
            model.status_id = status_id
            if comments is not None:
                model.comments = comments
            await self._session.flush()
            await self._session.refresh(model)
            
            self.log_info("Document status and comments updated successfully", 
                         document_id=document_id, 
                         new_status=status_id,
                         comments_updated=comments is not None)
            
            return _document_to_entity(model)
        except SQLAlchemyError as e:
            self.log_error("Database error updating document status", error=str(e), document_id=document_id)
            raise Exception(f"Error updating document status: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error updating document status", error=str(e), document_id=document_id)
            raise Exception(f"Unexpected error updating document status: {str(e)}")

    async def validate_document_rows(self, document_id: int, valid_skus: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Validate all rows in a bulk upload document using PostgreSQL stored function."""
        try:
            # Call the PostgreSQL stored function with CAST syntax (compatible with SQLAlchemy asyncpg)
            # Always call with both parameters, function handles NULL/empty array internally
            stmt = text("SELECT * FROM tottus_pe.fn_validate_agreements_bulk_upload_rows(CAST(:document_id AS integer), CAST(:valid_skus AS TEXT[]))")
            result = await self._session.execute(stmt, {
                "document_id": document_id,
                "valid_skus": valid_skus
            })
            
            # Get the result (should be a single row)
            row = result.fetchone()
            
            if row is None:
                self.log_warning("No result returned from validation function", document_id=document_id)
                return False, "Validation function returned no results"
            
            success = row.success
            message = row.message
            
            # Commit the transaction to persist the observations updates made by the stored function
            await self._session.flush()
            
            self.log_info("Document rows validation completed", 
                         document_id=document_id,
                         validation_success=success,
                         validation_message=message)
            
            return success, message
        except SQLAlchemyError as e:
            self.log_error("Database error validating document rows", error=str(e), document_id=document_id)
            raise Exception(f"Error validating document rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error validating document rows", error=str(e), document_id=document_id)
            raise Exception(f"Unexpected error during validation: {str(e)}")

    async def resolve_document_rows(self, document_id: int, resolved_by_user_email: str) -> Tuple[bool, str]:
        """Resolve all rows in a bulk upload document using PostgreSQL stored function."""
        try:
            # Call the PostgreSQL stored function
            stmt = text("SELECT * FROM tottus_pe.fn_resolve_agreements_bulk_upload_rows(:document_id, :resolved_by_user_email)")
            result = await self._session.execute(stmt, {
                "document_id": document_id,
                "resolved_by_user_email": resolved_by_user_email
            })
            
            # Get the result (should be a single row)
            row = result.fetchone()
            
            if row is None:
                self.log_warning("No result returned from resolution function", 
                               document_id=document_id,
                               resolved_by=resolved_by_user_email)
                return False, "Resolution function returned no results"
            
            success = row.success
            message = row.message
            
            # Flush changes made by the stored function within this session's transaction
            await self._session.flush()
            
            self.log_info("Document rows resolution completed", 
                         document_id=document_id,
                         resolved_by=resolved_by_user_email,
                         resolution_success=success,
                         resolution_message=message)
            
            return success, message
        except SQLAlchemyError as e:
            self.log_error("Database error resolving document rows", 
                          error=str(e), 
                          document_id=document_id,
                          resolved_by=resolved_by_user_email)
            raise Exception(f"Error resolving document rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error resolving document rows", 
                          error=str(e), 
                          document_id=document_id,
                          resolved_by=resolved_by_user_email)
            raise Exception(f"Unexpected error during resolution: {str(e)}")

    async def create_agreements_from_resolved_rows(self, document_id: int, created_by_user_email: str, skus: List[Sku]) -> Tuple[bool, str, int]:
        """
        Create agreements and related tables from resolved document rows.
        This operation is transactional - all agreements are created or none.
        """
        try:
            # Get document info for business_unit_id and source_system
            document = await self._session.get(AgreementsBulkUploadDocumentsModel, document_id)
            if not document:
                return False, "Document not found", 0
            
            # Create a lookup dictionary for SKUs by code for efficient access
            sku_lookup: Dict[str, Sku] = {sku.sku: sku for sku in skus}
            
            self.log_info("SKU lookup dictionary created for bulk operations", 
                         total_skus_provided=len(skus),
                         document_id=document_id)
            
            # Get all resolved rows for the document
            stmt = select(AgreementsBulkUploadDocumentRowsModel).where(
                AgreementsBulkUploadDocumentRowsModel.bulk_document_id == document_id,
                AgreementsBulkUploadDocumentRowsModel.active == True,
                AgreementsBulkUploadDocumentRowsModel.resolved_at.isnot(None)  # Only resolved rows
            ).order_by(AgreementsBulkUploadDocumentRowsModel.id)
            
            result = await self._session.execute(stmt)
            resolved_rows = result.scalars().all()
            
            if not resolved_rows:
                return False, "No resolved rows found for the document", 0
            
            self.log_info("Starting bulk agreements creation from resolved rows", 
                         document_id=document_id,
                         total_resolved_rows=len(resolved_rows),
                         created_by=created_by_user_email)
            
            # 1: Prepare all agreement data for bulk insert
            agreements_data = []
            products_data = []
            excluded_flags_data = []
            store_rules_data = []
            
            for row in resolved_rows:
                # Prepare main agreement data
                agreement_data = {
                    'business_unit_id': document.business_unit_id,
                    'start_date': row.start_date_parsed,
                    'end_date': row.end_date_parsed,
                    'agreement_type_id': None,  # Default agreement type
                    'status_id': AgreementStatusEnum.GENERATED.value,  # Use enum for status
                    'rebate_type_id': row.rebate_type_id,
                    'concept_id': row.concept_id,
                    'description': row.note,
                    'source_system': document.source_system,
                    'spf_code': row.spf_code,
                    'spf_description': row.spf_description,
                    'unit_price': row.unit_rebate_num or 0,
                    'billing_type': row.billing_type_id,
                    'pmm_username': row.pmm_user_id,
                    'store_grouping_id': row.group_id,
                    'currency_id': CurrencyEnum.PEN.value,
                    'bulk_upload_document_id': document_id,
                    'created_by_user_email': created_by_user_email,
                    'bulk_row_id': row.id  # Temporary field to map back to related tables
                }
                agreements_data.append(agreement_data)
                
                # Prepare agreement product data with enriched SKU information
                if row.sku:
                    sku_data = sku_lookup.get(row.sku)
                    
                    product_data = {
                        'sku_code': row.sku,
                        'sku_description': sku_data.descripcion_sku if sku_data else None,
                        'division_code': sku_data.codigo_division if sku_data else None,
                        'division_name': sku_data.division if sku_data else None,
                        'department_code': sku_data.codigo_departamento if sku_data else None,
                        'department_name': sku_data.departamento if sku_data else None,
                        'subdepartment_code': sku_data.codigo_subdepartamento if sku_data else None,
                        'subdepartment_name': sku_data.subdepartamento if sku_data else None,
                        'class_code': sku_data.codigo_clase if sku_data else None,
                        'class_name': sku_data.clase if sku_data else None,
                        'subclass_code': sku_data.codigo_subclase if sku_data else None,
                        'subclass_name': sku_data.subclase if sku_data else None,
                        'brand_id': str(sku_data.marca_id) if sku_data else None,
                        'brand_name': sku_data.marca if sku_data else None,
                        'supplier_id': sku_data.proveedor_id if sku_data else None,
                        'supplier_name': sku_data.proveedor if sku_data else None,
                        'supplier_ruc': sku_data.ruc_proveedor if sku_data else None,
                        'created_by_user_email': created_by_user_email,
                        'bulk_row_id': row.id  # Temporary field to map to agreement
                    }
                    products_data.append(product_data)
                
                # Prepare excluded flags data
                if row.excluded_flag_ids:
                    for flag_id in row.excluded_flag_ids:
                        excluded_flags_data.append({
                            'excluded_flag_id': flag_id,
                            'created_by_user_email': created_by_user_email,
                            'bulk_row_id': row.id  # Temporary field to map to agreement
                        })
                
                # Prepare store rules data (included stores)
                if row.included_store_ids:
                    for store_id in row.included_store_ids:
                        store_rules_data.append({
                            'store_id': store_id,
                            'status': StoreRuleStatusEnum.INCLUDE,
                            'created_by_user_email': created_by_user_email,
                            'bulk_row_id': row.id  # Temporary field to map to agreement
                        })
                
                # Prepare store rules data (excluded stores)
                if row.excluded_store_ids:
                    for store_id in row.excluded_store_ids:
                        store_rules_data.append({
                            'store_id': store_id,
                            'status': StoreRuleStatusEnum.EXCLUDE,
                            'created_by_user_email': created_by_user_email,
                            'bulk_row_id': row.id  # Temporary field to map to agreement
                        })
            
            # 2: Bulk insert agreements with returning IDs
            self.log_info("Performing bulk insert for agreements", 
                         agreements_count=len(agreements_data))

            # Remove temporary field from agreements data before insert
            for agreement_data in agreements_data:
                agreement_data.pop('bulk_row_id', None)
            
            # Bulk insert agreements and get their IDs back
            agreements_stmt = (
                AgreementModel.__table__.insert()
                .returning(AgreementModel.id)
            )
            agreements_result = await self._session.execute(agreements_stmt, agreements_data)
            agreement_ids = [row[0] for row in agreements_result.fetchall()]
            
            # 3: Map agreement IDs back to related data and bulk insert all related tables
            if products_data:
                # Map agreement IDs to product data
                for i, product_data in enumerate(products_data):
                    # Find the agreement ID for this row
                    row_id = product_data.pop('bulk_row_id')
                    row_index = next(j for j, row in enumerate(resolved_rows) if row.id == row_id)
                    product_data['agreement_id'] = agreement_ids[row_index]
                
                self.log_info("Performing bulk insert for agreement products", 
                             products_count=len(products_data))
                await self._session.execute(AgreementProductModel.__table__.insert(), products_data)
            
            if excluded_flags_data:
                # Map agreement IDs to excluded flags data
                for flag_data in excluded_flags_data:
                    row_id = flag_data.pop('bulk_row_id')
                    row_index = next(j for j, row in enumerate(resolved_rows) if row.id == row_id)
                    flag_data['agreement_id'] = agreement_ids[row_index]
                
                self.log_info("Performing bulk insert for excluded flags", 
                             excluded_flags_count=len(excluded_flags_data))
                await self._session.execute(AgreementExcludedFlagModel.__table__.insert(), excluded_flags_data)
            
            if store_rules_data:
                # Map agreement IDs to store rules data
                for store_rule_data in store_rules_data:
                    row_id = store_rule_data.pop('bulk_row_id')
                    row_index = next(j for j, row in enumerate(resolved_rows) if row.id == row_id)
                    store_rule_data['agreement_id'] = agreement_ids[row_index]
                
                self.log_info("Performing bulk insert for store rules", 
                             store_rules_count=len(store_rules_data))
                await self._session.execute(AgreementStoreRuleModel.__table__.insert(), store_rules_data)
            
            # 4: Single flush at the end instead of individual flushes
            await self._session.flush()
            
            agreements_created = len(agreement_ids)
            success_message = f"Successfully created {agreements_created} agreements with all related tables using bulk operations"
            self.log_info("Bulk agreements creation completed successfully", 
                         document_id=document_id,
                         agreements_created=agreements_created,
                         created_by=created_by_user_email,
                         products_created=len(products_data),
                         excluded_flags_created=len(excluded_flags_data),
                         store_rules_created=len(store_rules_data))
            
            return True, success_message, agreements_created
            
        except SQLAlchemyError as e:
            self.log_error("Database error creating agreements from resolved rows", 
                          error=str(e), 
                          document_id=document_id,
                          created_by=created_by_user_email)
            raise Exception(f"Error creating agreements from resolved rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error creating agreements from resolved rows", 
                          error=str(e), 
                          document_id=document_id,
                          created_by=created_by_user_email)
            raise Exception(f"Unexpected error creating agreements from resolved rows: {str(e)}")

    async def get_document_with_rows(self, document_id: int) -> Tuple[Optional[AgreementsBulkUploadDocument], List[AgreementsBulkUploadDocumentRow]]:
        """
        Get document and its rows in a single database operation to optimize connection usage.
        This method reduces database connections from 2 to 1 for bulk operations.
        """
        try:
            # Get document first
            document_model = await self._session.get(AgreementsBulkUploadDocumentsModel, document_id)
            
            if document_model is None:
                self.log_info("Document not found during optimized retrieval", document_id=document_id)
                return None, []
            
            # Get document rows in the same session
            stmt = select(AgreementsBulkUploadDocumentRowsModel).where(
                AgreementsBulkUploadDocumentRowsModel.bulk_document_id == document_id
            ).order_by(AgreementsBulkUploadDocumentRowsModel.id)
            
            result = await self._session.execute(stmt)
            rows_models = result.scalars().all()
            
            # Convert to entities
            document_entity = _document_to_entity(document_model)
            rows_entities = [_row_to_entity(row_model) for row_model in rows_models]
            
            self.log_info("Document with rows retrieved successfully in single operation", 
                         document_id=document_id,
                         total_rows=len(rows_entities))
            
            return document_entity, rows_entities
            
        except SQLAlchemyError as e:
            self.log_error("Database error getting document with rows in single operation", 
                          error=str(e), 
                          document_id=document_id)
            raise Exception(f"Error getting document with rows: {str(e)}")
        except Exception as e:
            self.log_error("Unexpected error getting document with rows in single operation", 
                          error=str(e), 
                          document_id=document_id)
            raise Exception(f"Unexpected error getting document with rows: {str(e)}")
