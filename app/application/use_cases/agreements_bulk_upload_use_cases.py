"""Agreements bulk upload use cases for business logic."""

import time
from typing import Dict, List

from fastapi import UploadFile

from app.interfaces.schemas.agreements_bulk_upload_schema import (
    BulkUploadRequest,
    BulkUploadProcessResponse,
    BulkUploadDocumentResponse,
    BulkUploadDocumentResolutionResponse,
    AgreementsBulkUploadDocumentSchema,
    TemplateDownloadResponse
)
from app.domain.entities.agreements_bulk_upload import (
    AgreementsBulkUploadDocument,
    AgreementsBulkUploadDocumentRow
)
from app.domain.repositories.agreements_bulk_upload_repository import AgreementsBulkUploadRepository
from app.domain.repositories.sku_repository import SkuRepository
from app.core.utils import ExcelProcessing
from app.core.utils.excel_processing import HeaderStyle
from app.core.logging import LoggerMixin
from app.core.agreement_enums import AgreementBulkUploadStatusEnum, SourceSystemEnum
from app.interfaces.schemas.security_schema import User
from app.core.constants import BULK_UPLOAD_TEMPLATES
from app.core.cloud_strategy import CloudContext, AzureBlobStrategy
from app.core.helpers import get_azure_container_name


class AgreementsBulkUploadUseCases(LoggerMixin):
    """Use cases for agreements bulk upload operations."""

    # Column mapping for SPF source system
    SPF_COLUMN_MAPPING = {
        'pmm_user': ['USUARIO PMM'],
        'group_name': ['AGRUPACION'],
        'excluded_flags': ['BANDERAS EXCLUIDAS'],
        'included_stores': ['TIENDAS INCLUIDAS'],
        'excluded_stores': ['TIENDAS EXCLUIDAS'],
        'rebate_type': ['TIPO DE REBATE'],
        'concept': ['CONCEPTO'],
        'note': ['GLOSA'],
        'spf_code': ['CODIGO SPF'],
        'spf_description': ['DESCRIPCION SPF'],
        'sku': ['SKU'],
        'start_date': ['FECHA DE INICIO'],
        'end_date': ['FECHA DE FIN'],
        'unit_rebate_pen': ['RECO UNITARIO (S/)'],
        'billing_type': ['TIPO DE FACTURACIÓN']
    }

    # Field types for SPF source system
    SPF_FIELD_TYPES = {
        'pmm_user': 'string',
        'group_name': 'string',
        'excluded_flags': 'string',
        'included_stores': 'text',
        'excluded_stores': 'text',
        'rebate_type': 'string',
        'concept': 'string',
        'note': 'string',
        'spf_code': 'string',
        'spf_description': 'string',
        'sku': 'string',
        'start_date': 'string',
        'end_date': 'string',
        'unit_rebate_pen': 'string',
        'billing_type': 'string'
    }

    # Required fields for SPF source system (all except optional ones)
    SPF_REQUIRED_FIELDS = [
        'pmm_user', 'group_name', 'rebate_type', 'concept', 'note', 
        'spf_code', 'sku', 'start_date', 'end_date', 
        'unit_rebate_pen', 'billing_type'
    ]

    # Optional fields for SPF source system
    SPF_OPTIONAL_FIELDS = [
        'excluded_flags', 'included_stores', 'excluded_stores', 'spf_description'
    ]

    # Column mapping for PMM source system (without SPF-specific fields)
    PMM_COLUMN_MAPPING = {
        'pmm_user': ['USUARIO PMM'],
        'group_name': ['AGRUPACION'],
        'excluded_flags': ['BANDERAS EXCLUIDAS'],
        'included_stores': ['TIENDAS INCLUIDAS'],
        'excluded_stores': ['TIENDAS EXCLUIDAS'],
        'rebate_type': ['TIPO DE REBATE'],
        'concept': ['CONCEPTO'],
        'note': ['GLOSA'],
        'sku': ['SKU'],
        'start_date': ['FECHA DE INICIO'],
        'end_date': ['FECHA DE FIN'],
        'unit_rebate_pen': ['RECO UNITARIO (S/)'],
        'billing_type': ['TIPO DE FACTURACIÓN']
    }

    # Field types for PMM source system (without SPF-specific fields)
    PMM_FIELD_TYPES = {
        'pmm_user': 'string',
        'group_name': 'string',
        'excluded_flags': 'string',
        'included_stores': 'text',
        'excluded_stores': 'text',
        'rebate_type': 'string',
        'concept': 'string',
        'note': 'string',
        'sku': 'string',
        'start_date': 'string',
        'end_date': 'string',
        'unit_rebate_pen': 'string',
        'billing_type': 'string'
    }

    # Required fields for PMM source system (all except optional ones)
    PMM_REQUIRED_FIELDS = [
        'pmm_user', 'group_name', 'rebate_type', 'concept', 'note', 
        'sku', 'start_date', 'end_date', 'unit_rebate_pen', 'billing_type'
    ]

    # Optional fields for PMM source system
    PMM_OPTIONAL_FIELDS = [
        'excluded_flags', 'included_stores', 'excluded_stores'
    ]

    def __init__(
        self, 
        bulk_upload_repository: AgreementsBulkUploadRepository,
        excel_service: ExcelProcessing,
        sku_repository: SkuRepository
    ):
        """Initialize bulk upload use cases with repository and utilities."""
        self.bulk_upload_repository = bulk_upload_repository
        self.excel_service = excel_service
        self.sku_repository = sku_repository

    def _get_column_configuration(self, source_system_type: SourceSystemEnum) -> tuple:
        """
        Get column mapping, field types, sheet name and required fields based on source system type.
        
        Args:
            source_system_type: The source system type (SPF or PMM)
            
        Returns:
            tuple: (column_mapping, field_types, sheet_name, required_fields)
        """
        if source_system_type == SourceSystemEnum.SPF:
            return (
                self.SPF_COLUMN_MAPPING, 
                self.SPF_FIELD_TYPES, 
                'Plantilla SPF',
                self.SPF_REQUIRED_FIELDS
            )
        elif source_system_type == SourceSystemEnum.PMM:
            return (
                self.PMM_COLUMN_MAPPING, 
                self.PMM_FIELD_TYPES, 
                'Plantilla PMM',
                self.PMM_REQUIRED_FIELDS
            )
        else:
            raise ValueError(f"Unsupported source system type: {source_system_type}")

    async def process_bulk_upload(
        self, 
        request: BulkUploadRequest, 
        file: UploadFile,
        user: User
    ) -> BulkUploadProcessResponse:
        """Process bulk upload Excel file and create document with rows."""
        start_time = time.time()
        
        self.log_info("Starting bulk upload process", 
                     file_name=file.filename,
                     source_system_type=request.source_system_type.value,
                     user_email=user.email)
        
        try:
            # Validation of source_system_type is handled automatically by Pydantic schema using SourceSystemEnum
            
            # Get appropriate column configuration based on source system type
            column_mapping, field_types, sheet_name, required_fields = self._get_column_configuration(request.source_system_type)
            
            self.log_info("Using configuration for source system", 
                         source_system=request.source_system_type.value,
                         sheet_name=sheet_name,
                         total_columns=len(column_mapping),
                         required_fields_count=len(required_fields))
            
            # Step 1: Validate Excel file
            if not await self.excel_service.validate_excel_file(file):
                processing_time = time.time() - start_time
                
                self.log_warning("Invalid Excel file format, returning early", 
                               file_name=file.filename)
                
                return BulkUploadProcessResponse(
                    document_id=0,  # No document created
                    document_uid=None,
                    total_rows_processed=0,
                    valid_rows=0,
                    invalid_rows=0,
                    processing_status="INVALID_FILE_FORMAT",
                    file_name=file.filename or "unknown",
                    processing_time_seconds=round(processing_time, 2),
                    validation_errors=["Invalid Excel file format"],
                    final_status=AgreementBulkUploadStatusEnum.ERROR.value
                )
            
            # Step 1.5: Get available sheets for debugging
            available_sheets = await self.excel_service.get_excel_sheets(file)
            self.log_info("Available Excel sheets", 
                         sheets=available_sheets,
                         target_sheet=sheet_name)
            
            # Step 2: Process Excel file with specific sheet and required fields validation
            processed_rows, format_validation_errors = await self.excel_service.process_excel_file(
                file=file,
                sheet_name=sheet_name,
                column_mapping=column_mapping,
                field_types=field_types,
                required_fields=required_fields
            )
            
            # If format validation errors found, return early with structured response
            if format_validation_errors:
                processing_time = time.time() - start_time
                
                self.log_warning("Format validation errors found, returning early", 
                               error_count=len(format_validation_errors),
                               errors=format_validation_errors)
                
                return BulkUploadProcessResponse(
                    document_id=0,  # No document created
                    document_uid=None,
                    total_rows_processed=0,
                    valid_rows=0,
                    invalid_rows=len(processed_rows) if processed_rows else 0,
                    processing_status="FORMAT_VALIDATION_FAILED",
                    file_name=file.filename or "unknown",
                    processing_time_seconds=round(processing_time, 2),
                    validation_errors=format_validation_errors,
                    final_status=AgreementBulkUploadStatusEnum.ERROR.value
                )
            
            # Step 3: Create document            
            document = AgreementsBulkUploadDocument.create(
                business_unit_id=user.bu_id,  # User business unit ID
                status_id=AgreementBulkUploadStatusEnum.IN_PROGRESS.value,
                created_by_user_email=user.email,
                source_system=request.source_system_type,  # Include source system
                comments=None
            )
            
            created_document = await self.bulk_upload_repository.create_document(document)
            
            self.log_info("Bulk upload document created", 
                        document_id=created_document.id,
                        document_uid=str(created_document.document_uid))
        
            # Step 4: Create document rows
            document_rows = []
            for row_data in processed_rows:
                row = AgreementsBulkUploadDocumentRow.create(
                    bulk_document_id=created_document.id,
                    created_by_user_email=user.email,
                    **row_data
                )
                document_rows.append(row)
            
            # Initialize validation variables
            validation_success = True
            validation_message = "No data to validate"
            
            if document_rows:
                await self.bulk_upload_repository.create_document_rows(document_rows)
                self.log_info("Document rows created successfully", 
                            document_id=created_document.id,
                            total_rows=len(document_rows))
                
                # Step 4.1: Get SKU codes and validate them using SKU repository
                sku_codes = []
                for row in document_rows:
                    if row.sku and row.sku.strip():  # Only include non-empty SKU codes
                        sku_codes.append(row.sku.strip())
                
                # Remove duplicates while preserving order
                unique_sku_codes = list(dict.fromkeys(sku_codes))
                
                valid_skus = []
                if unique_sku_codes:
                    self.log_info("Fetching SKU validation data", 
                                sku_count=len(unique_sku_codes),
                                document_id=created_document.id)
                    
                    # Get SKUs from BigQuery
                    sku_entities = await self.sku_repository.get_skus_by_codes(unique_sku_codes)
                    valid_skus = [sku.sku for sku in sku_entities if sku.sku]
                    
                    self.log_info("SKU validation data retrieved", 
                                requested_skus=len(unique_sku_codes),
                                valid_skus_found=len(valid_skus),
                                document_id=created_document.id)
                
                # Step 4.2: Validate document rows using business rules with SKU validation
                validation_success, validation_message = await self.bulk_upload_repository.validate_document_rows(
                    created_document.id, 
                    valid_skus if valid_skus else None
                )
                self.log_info("Document rows validation completed", 
                            document_id=created_document.id,
                            validation_success=validation_success,
                            validation_message=validation_message,
                            sku_validation_length=len(valid_skus))
            else:
                # No rows to process
                validation_success = False
                validation_message = "No data rows found to process"
                self.log_warning("No document rows to create", 
                               document_id=created_document.id,
                               processed_rows_count=len(processed_rows))
            
            
            # Step 5: Update document status based on processing results
            # Determine final status based on validation results
            if not document_rows:
                # No data rows to process
                final_status_enum = AgreementBulkUploadStatusEnum.ERROR  # "5" - No data to process
                processing_status_description = "NO_DATA"
            elif validation_success:
                # All validations passed successfully
                final_status_enum = AgreementBulkUploadStatusEnum.PARTIAL_LOADED  # "4" - Data loaded successfully
                processing_status_description = "COMPLETED"
            else:
                # Business rules validation failed (but data was processed and stored)
                final_status_enum = AgreementBulkUploadStatusEnum.ERROR  # "5" - Data loaded with errors
                processing_status_description = "COMPLETED_WITH_OBSERVATIONS"

            # Log status update
            self.log_info("Setting document status", 
                        document_id=created_document.id,
                        status_id=final_status_enum.value,
                        status_name=final_status_enum.name,
                        description=processing_status_description,
                        validation_success=validation_success,
                        validation_message=validation_message)
            
            await self.bulk_upload_repository.update_document_status(
                created_document.id, 
                final_status_enum.value,
                f"Processing completed - {processing_status_description}. Validation: {'Passed' if validation_success else 'Failed'}"
            )
            
            processing_time = time.time() - start_time
            
            response = BulkUploadProcessResponse(
                document_id=created_document.id,
                document_uid=created_document.document_uid,
                total_rows_processed=len(processed_rows),
                valid_rows=len(processed_rows) if validation_success else 0,
                invalid_rows=0 if validation_success else len(processed_rows),
                processing_status=processing_status_description,
                file_name=file.filename or "unknown",
                processing_time_seconds=round(processing_time, 2),
                validation_errors=[validation_message] if not validation_success else [],
                final_status=final_status_enum.value
            )
            
            self.log_info("Bulk upload process completed", 
                         document_id=created_document.id,
                         processing_time=processing_time,
                         total_rows=response.total_rows_processed,
                         valid_rows=response.valid_rows,
                         invalid_rows=response.invalid_rows,
                         final_status=final_status_enum.value,
                         status_description=processing_status_description,
                         validation_success=validation_success)
            
            return response
            
        except Exception as e:
            self.log_error("Error in bulk upload process", 
                          error=str(e),
                          file_name=file.filename,
                          user_email=user.email)
            raise

    async def get_document_by_id(self, document_id: int) -> BulkUploadDocumentResponse:
        """
        Get bulk upload document by ID with row count.
        """
        self.log_info("Getting bulk upload document", document_id=document_id)
        
        try:
            # Get document
            document = await self.bulk_upload_repository.get_document_by_id(document_id)
            if document is None:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Get row count
            rows = await self.bulk_upload_repository.get_document_rows(document_id)
            
            # Convert to schema
            document_schema = AgreementsBulkUploadDocumentSchema.model_validate(document)
            
            response = BulkUploadDocumentResponse(
                document=document_schema,
                total_rows=len(rows)
            )
            
            self.log_info("Document retrieved successfully", 
                         document_id=document_id,
                         total_rows=response.total_rows)
            
            return response
            
        except Exception as e:
            self.log_error("Error getting bulk upload document", 
                          error=str(e),
                          document_id=document_id)
            raise

    async def resolve_document_data(self, document_id: int, user: User) -> BulkUploadDocumentResolutionResponse:
        """Resolve document data by processing all rows and creating agreements."""
        start_time = time.time()
        
        self.log_info("Starting optimized document data resolution", 
                     document_id=document_id,
                     resolved_by=user.email)
         
        try:
            # 1: Get document and rows in single database call to avoid multiple connections
            document, document_rows = await self.bulk_upload_repository.get_document_with_rows(document_id)
            if document is None:
                raise ValueError(f"Document with ID {document_id} not found")
            
            self.log_info("Document and rows retrieved in single operation", 
                         document_id=document_id,
                         current_status=document.status_id,
                         total_rows=len(document_rows),
                         document_uid=str(document.document_uid))
            
            # 2: Extract SKU codes early from existing rows (no additional DB call needed)
            sku_codes = []
            for row in document_rows:
                if row.sku and row.sku.strip():
                    sku_codes.append(row.sku.strip())
            
            # Remove duplicates while preserving order
            unique_sku_codes = list(dict.fromkeys(sku_codes))
            
            # 3: Get SKU entities in parallel with resolution (before resolution completes)
            skus = []
            if unique_sku_codes:
                self.log_info("Fetching SKU data for agreement product enrichment", 
                            sku_count=len(unique_sku_codes),
                            document_id=document_id)
                
                sku_entities = await self.sku_repository.get_skus_by_codes(unique_sku_codes)
                skus = sku_entities
                
                self.log_info("SKU data retrieved for agreement enrichment", 
                            requested_skus=len(unique_sku_codes),
                            found_skus=len(skus),
                            document_id=document_id)
            else:
                self.log_info("No SKUs found in document rows for enrichment", 
                            document_id=document_id)
            
            # Call repository method to resolve document rows
            resolution_success, resolution_message = await self.bulk_upload_repository.resolve_document_rows(
                document_id=document_id,
                resolved_by_user_email=user.email
            )
            
            self.log_info("Document resolution completed", 
                         document_id=document_id,
                         resolution_success=resolution_success,
                         resolution_message=resolution_message,
                         resolved_by=user.email)
            
            # If resolution was successful, create agreements from resolved rows
            agreements_created_count = 0
            agreement_creation_success = False
            if resolution_success:
                self.log_info("Resolution successful, creating agreements from resolved rows with optimized bulk operations", 
                             document_id=document_id)
                
                try:
                    # 4: Pass pre-fetched SKUs directly (no additional DB calls or processing needed)
                    agreement_creation_success, agreement_message, agreements_created_count = await self.bulk_upload_repository.create_agreements_from_resolved_rows(
                        document_id=document_id,
                        created_by_user_email=user.email,
                        skus=skus
                    )
                    
                    self.log_info("Agreement creation completed", 
                                 document_id=document_id,
                                 creation_success=agreement_creation_success,
                                 agreements_created=agreements_created_count,
                                 creation_message=agreement_message)
                    
                    # Update the resolution message to include agreement creation info
                    if agreement_creation_success:
                        resolution_message = f"{resolution_message}. Created {agreements_created_count} agreements successfully."
                        
                        # Update document status to UPLOADED since agreements were created successfully
                        await self.bulk_upload_repository.update_document_status(
                            document_id, 
                            AgreementBulkUploadStatusEnum.UPLOADED.value,
                            f"Document processed successfully. Created {agreements_created_count} agreements."
                        )
                        self.log_info("Document status updated to UPLOADED after successful agreement creation", 
                                     document_id=document_id,
                                     new_status=AgreementBulkUploadStatusEnum.UPLOADED.value)
                    else:
                        resolution_message = f"{resolution_message}. Agreement creation failed: {agreement_message}"
                        resolution_success = False  # Mark overall process as failed
                        
                        # Update document status to ERROR since agreement creation failed
                        await self.bulk_upload_repository.update_document_status(
                            document_id, 
                            AgreementBulkUploadStatusEnum.ERROR.value,
                            f"Agreement creation failed: {agreement_message}"
                        )
                        self.log_warning("Document status updated to ERROR due to agreement creation failure", 
                                        document_id=document_id,
                                        new_status=AgreementBulkUploadStatusEnum.ERROR.value)
                        
                except Exception as e:
                    self.log_error("Error during agreement creation", 
                                 error=str(e),
                                 document_id=document_id)
                    resolution_message = f"{resolution_message}. Agreement creation failed: {str(e)}"
                    resolution_success = False
                    
                    # Update document status to ERROR due to exception
                    await self.bulk_upload_repository.update_document_status(
                        document_id, 
                        AgreementBulkUploadStatusEnum.ERROR.value,
                        f"Exception during agreement creation: {str(e)}"
                    )
                    self.log_error("Document status updated to ERROR due to agreement creation exception", 
                                  document_id=document_id,
                                  new_status=AgreementBulkUploadStatusEnum.ERROR.value)
            else:
                # Resolution failed, update document status to ERROR
                await self.bulk_upload_repository.update_document_status(
                    document_id, 
                    AgreementBulkUploadStatusEnum.ERROR.value,
                    f"Resolution failed: {resolution_message}"
                )
                self.log_warning("Document status updated to ERROR due to resolution failure", 
                                document_id=document_id,
                                new_status=AgreementBulkUploadStatusEnum.ERROR.value)
            
            # Get updated document status only if needed (status may have changed)
            updated_document = await self.bulk_upload_repository.get_document_by_id(document_id)
            if updated_document is None:
                raise Exception(f"Failed to retrieve updated document {document_id}")
            
            # Convert to schema
            document_schema = AgreementsBulkUploadDocumentSchema.model_validate(updated_document)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            response = BulkUploadDocumentResolutionResponse(
                document=document_schema,
                total_rows=len(document_rows),  # Use pre-fetched rows count
                resolution_success=resolution_success,
                resolution_message=resolution_message,
                agreements_created=agreements_created_count,
                agreements_creation_success=agreement_creation_success,
                processing_time_seconds=round(processing_time, 2)
            )
            
            self.log_info("Document data resolution completed successfully with optimizations", 
                         document_id=document_id,
                         final_status=updated_document.status_id,
                         total_rows=len(document_rows),  # Use pre-fetched rows count
                         resolution_success=resolution_success,
                         agreements_created=agreements_created_count,
                         agreements_creation_success=agreement_creation_success,
                         processing_time=processing_time)
            
            return response
            
        except Exception as e:
            self.log_error("Error resolving document data", 
                          error=str(e),
                          document_id=document_id,
                          resolved_by=user.email)
            raise

    async def get_template_download_url(self, source_system_type: str, user: User) -> TemplateDownloadResponse:
        """Get download URL for bulk upload template."""
        
        # Validate source system type
        if source_system_type.upper() not in BULK_UPLOAD_TEMPLATES:
            available_types = list(BULK_UPLOAD_TEMPLATES.keys())
            raise ValueError(f"Invalid source system type. Available types: {', '.join(available_types)}")
        
        # Get template path
        template_key = source_system_type.upper()
        template_path = BULK_UPLOAD_TEMPLATES[template_key]

        # Configure expiration time (10 minutes for templates)
        expiry_minutes = 10
        
        # Generate download URL using cloud strategy with custom expiry
        ctx = CloudContext(AzureBlobStrategy())
        container_name = get_azure_container_name(user.country)
        url_sas = ctx.get_url_file(template_path, container_name, expiry_minutes)
        
        # Create template file name
        template_name = f"plantilla_{source_system_type.lower()}_v1.xlsx"
        
        return TemplateDownloadResponse(
            source_system_type=source_system_type.upper(),
            template_name=template_name,
            download_url=url_sas,
            expires_in_minutes=expiry_minutes  # Now matches the actual SAS URL expiry
        )

    async def get_document_rows_download_url(self, document_id: int, user: User) -> TemplateDownloadResponse:
        """Generate Excel file from document rows and return download URL."""
        
        # Optimized: Get document and rows in single database operation to prevent connection exhaustion
        document, rows = await self.bulk_upload_repository.get_document_with_rows(document_id)
        
        if document is None:
            raise ValueError(f"Document with ID {document_id} not found")
        
        if not rows:
            raise ValueError(f"No rows found for document {document_id}")
        
        self.log_info("Document and rows retrieved successfully for export", 
                     document_id=document_id,
                     total_rows=len(rows))
        
        # Generate Excel content from rows
        excel_buffer = await self._create_excel_from_rows(rows, document)
        
        # Configure expiration time (30 minutes for document exports)
        expiry_minutes = 30
        
        # Upload to temp folder in cloud storage
        timestamp = int(time.time())
        temp_file_path = f"temp/document_exports/document_{document_id}_rows_{timestamp}.xlsx"
        
        ctx = CloudContext(AzureBlobStrategy())
        container_name = get_azure_container_name(user.country)
        
        # Upload the Excel file
        upload_result = ctx.upload_bytes(excel_buffer, temp_file_path, container_name)
        
        self.log_info("Document rows Excel file uploaded successfully", 
                     document_id=document_id,
                     temp_file_path=temp_file_path,
                     file_size=len(excel_buffer))
        
        # Generate download URL
        url_sas = ctx.get_url_file(temp_file_path, container_name, expiry_minutes)
        
        # Create response file name
        file_name = f"document_{document_id}_rows_export.xlsx"
        
        return TemplateDownloadResponse(
            source_system_type=document.source_system,
            template_name=file_name,
            download_url=url_sas,
            expires_in_minutes=expiry_minutes
        )

    async def _create_excel_from_rows(self, rows: List[AgreementsBulkUploadDocumentRow], document: AgreementsBulkUploadDocument) -> bytes:
        """Create Excel file from document rows with observations."""
        
        # Define headers based on source system
        if document.source_system == SourceSystemEnum.SPF:
            headers = [
                "USUARIO PMM", "AGRUPACION", "BANDERAS EXCLUIDAS", 
                "TIENDAS INCLUIDAS", "TIENDAS EXCLUIDAS", "TIPO DE REBATE",
                "CONCEPTO", "GLOSA", "CODIGO SPF", "DESCRIPCION SPF", 
                "SKU", "FECHA DE INICIO", "FECHA DE FIN", 
                "RECO UNITARIO (S/)", "TIPO DE FACTURACIÓN", "OBSERVACIONES"
            ]
        else:  # PMM
            headers = [
                "USUARIO PMM", "AGRUPACION", "BANDERAS EXCLUIDAS",
                "TIENDAS INCLUIDAS", "TIENDAS EXCLUIDAS", "TIPO DE REBATE",
                "CONCEPTO", "GLOSA", "SKU", "FECHA DE INICIO", "FECHA DE FIN",
                "RECO UNITARIO (S/)", "TIPO DE FACTURACIÓN", "OBSERVACIONES"
            ]
        
        # Prepare rows data
        rows_data = []
        for row in rows:
            if document.source_system == SourceSystemEnum.SPF:
                row_data = [
                    row.pmm_user, row.group_name, row.excluded_flags,
                    row.included_stores, row.excluded_stores, row.rebate_type,
                    row.concept, row.note, row.spf_code, row.spf_description,
                    row.sku, row.start_date, row.end_date,
                    row.unit_rebate_pen, row.billing_type, row.observations
                ]
            else:  # PMM
                row_data = [
                    row.pmm_user, row.group_name, row.excluded_flags,
                    row.included_stores, row.excluded_stores, row.rebate_type,
                    row.concept, row.note, row.sku, row.start_date, row.end_date,
                    row.unit_rebate_pen, row.billing_type, row.observations
                ]
            rows_data.append(row_data)
        
        # Use the generic Excel creation method with custom styling
        header_styles = self._create_header_styles_for_document(document.source_system, headers)
        sheet_name = f"Plantilla {document.source_system.value}"
        return await self.excel_service.create_excel_from_data(
            headers=headers,
            rows_data=rows_data,
            sheet_name=sheet_name,
            apply_styling=True,
            header_styles=header_styles
        )

    def _create_header_styles_for_document(self, source_system: SourceSystemEnum, headers: List[str]) -> Dict[str, HeaderStyle]:
        """Create custom header styles for document export based on column importance."""
        # Define different styles for different types of columns
        styles = {}
        
        for header in headers:
            if header in ["USUARIO PMM", "AGRUPACION", "TIPO DE REBATE", "CONCEPTO", "GLOSA", "CODIGO SPF", "SKU", "FECHA DE INICIO", "FECHA DE FIN", "RECO UNITARIO (S/)", "TIPO DE FACTURACIÓN"]:
                # red theme (important info)
                styles[header] = HeaderStyle.create_custom(
                    bold=True,
                    font_color="FFFFFF",
                    background_color="FF0000",  # red
                    horizontal_alignment="center"
                )
            elif header in ["BANDERAS EXCLUIDAS", "TIENDAS INCLUIDAS", "TIENDAS EXCLUIDAS", "DESCRIPCION SPF"]:
                # Green theme (optional info)
                styles[header] = HeaderStyle.create_custom(
                    bold=True,
                    font_color="000000", 
                    background_color="C4D79B",  # Green
                    horizontal_alignment="center"
                )
            else:
                # Default columns - Default blue theme
                styles[header] = HeaderStyle.create_default()
        
        return styles
