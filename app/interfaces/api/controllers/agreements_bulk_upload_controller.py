"""Agreements bulk upload controllers for the API interface."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from app.core.agreement_enums import AgreementBulkUploadStatusEnum
from app.interfaces.schemas.agreements_bulk_upload_schema import (
    BulkUploadProcessResponse,
    BulkUploadDocumentResponse,
    BulkUploadDocumentResolutionResponse,
    TemplateDownloadResponse
)
from app.core.response import (
    SuccessResponse,
    create_error_response,
    create_success_response,
)
from app.interfaces.schemas.security_schema import Roles, User
from app.interfaces.dependencies.agreements_bulk_upload_dependencies import BulkUploadUseCasesDep
from app.interfaces.dependencies.headers import get_country_header, security_scheme
from app.interfaces.dependencies.auth_dependencies import check_db_permissions_simple
from app.core.logging import LoggerMixin

router = APIRouter(
    prefix="/v1/agreements-bulk-upload",
    tags=["agreements-bulk-upload"],
    dependencies=[
        Depends(get_country_header),
        Depends(security_scheme)
    ]
)

# ---------------------------
# Class-based Controller
# ---------------------------
class AgreementsBulkUploadController(LoggerMixin):
    """Controller for agreements bulk upload operations."""

    async def upload_bulk_agreements(
        self,
        request: Request,
        file: UploadFile,
        source_system_type: str,
        bulk_upload_use_cases: BulkUploadUseCasesDep
    ) -> SuccessResponse[BulkUploadProcessResponse]:
        """
        Upload and process Excel file for bulk agreements creation.
        """
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.BULK_UPLOAD_AGREEMENTS])

            # Validate input using Pydantic schema
            from app.interfaces.schemas.agreements_bulk_upload_schema import BulkUploadRequest
            upload_request = BulkUploadRequest(
                source_system_type=source_system_type
            )

            self.log_info("Starting bulk upload request", 
                         file_name=file.filename,
                         source_system_type=upload_request.source_system_type.value,
                         user_email=user.email)

            # Validate file type
            if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=create_error_response(
                        message="File must be an Excel file (.xlsx or .xls)"
                    ).model_dump(),
                )

            # Process bulk upload using validated request
            result = await bulk_upload_use_cases.process_bulk_upload(
                request=upload_request,
                file=file,
                user=user
            )

            self.log_info("Bulk upload completed successfully", 
                         document_id=result.document_id,
                         valid_rows=result.valid_rows,
                         invalid_rows=result.invalid_rows,
                         final_status=result.final_status)

            # Determine success based on final_status
            # success = True only if all rows were processed without errors (PARTIAL_LOADED)
            success = result.final_status == AgreementBulkUploadStatusEnum.PARTIAL_LOADED.value
            
            # Set message based on success status
            if success:
                message = f"Bulk upload processed successfully. Document ID: {result.document_id}"
            else:
                if result.invalid_rows > 0 and result.valid_rows > 0:
                    message = f"Bulk upload completed with errors. Document ID: {result.document_id}. {result.valid_rows} rows processed, {result.invalid_rows} rows failed."
                elif result.invalid_rows > 0 and result.valid_rows == 0:
                    message = f"Bulk upload failed. Document ID: {result.document_id}. All {result.invalid_rows} rows had validation errors."
                else:
                    message = f"Bulk upload completed with issues. Document ID: {result.document_id}"

            return SuccessResponse(
                success=success,
                data=result,
                message=message
            )

        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning("Validation error in bulk upload", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error("Unexpected error in bulk upload", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Failed to process bulk upload").model_dump(),
            )

    async def get_bulk_upload_document(
        self,
        request: Request,
        document_id: int,
        bulk_upload_use_cases: BulkUploadUseCasesDep
    ) -> SuccessResponse[BulkUploadDocumentResponse]:
        """
        Get bulk upload document information by ID.
        """
        try:
            # Get user from middleware
            user: User = request.state.user  # noqa: F841

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_BULK_UPLOAD_AGREEMENTS])

            self.log_info("Getting bulk upload document", document_id=document_id)

            # Validate document ID
            if document_id <= 0:
                raise ValueError("Document ID must be greater than 0")

            # Get document
            document_data = await bulk_upload_use_cases.get_document_by_id(document_id)

            return create_success_response(
                data=document_data,
                message=f"Document {document_id} retrieved successfully"
            )

        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning("Validation error getting document", error=str(e), document_id=document_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error("Unexpected error getting document", error=str(e), document_id=document_id)
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(message=str(e)).model_dump(),
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=create_error_response(message="Failed to retrieve document").model_dump(),
                )

    async def resolve_bulk_upload_document(
        self,
        request: Request,
        document_id: int,
        bulk_upload_use_cases: BulkUploadUseCasesDep
    ) -> SuccessResponse[BulkUploadDocumentResolutionResponse]:
        """
        Resolve bulk upload document by processing all rows and creating agreements.
        """
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.BULK_UPLOAD_AGREEMENTS])

            self.log_info("Starting document resolution", 
                         document_id=document_id,
                         resolved_by=user.email)

            # Validate document ID
            if document_id <= 0:
                raise ValueError("Document ID must be greater than 0")

            # Resolve document data
            document_data = await bulk_upload_use_cases.resolve_document_data(document_id, user)

            # Create dynamic success message based on resolution results
            if document_data.agreements_creation_success:
                message = f"Document {document_id} resolved and {document_data.agreements_created} agreements created successfully"
            elif document_data.resolution_success:
                message = f"Document {document_id} resolved successfully but no agreements were created"
            else:
                message = f"Document {document_id} processing completed with issues: {document_data.resolution_message}"

            return SuccessResponse(
                success=document_data.resolution_success,
                data=document_data,
                message=message
            )

        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning("Validation error resolving document", 
                           error=str(e), 
                           document_id=document_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error("Unexpected error resolving document", 
                          error=str(e), 
                          document_id=document_id)
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(message=str(e)).model_dump(),
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=create_error_response(message="Failed to resolve document").model_dump(),
                )

    async def get_template_download_url(
        self,
        request: Request,
        source_system_type: str,
        bulk_upload_use_cases: BulkUploadUseCasesDep
    ) -> SuccessResponse[TemplateDownloadResponse]:
        """Get download URL for bulk upload template."""
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_BULK_UPLOAD_AGREEMENTS])

            self.log_info("Getting template download URL", 
                         source_system_type=source_system_type,
                         user_email=user.email)

            # Get template download data
            template_data = await bulk_upload_use_cases.get_template_download_url(source_system_type, user)

            self.log_info("Template download URL generated successfully", 
                         source_system_type=source_system_type,
                         template_name=template_data.template_name,
                         expires_in_minutes=template_data.expires_in_minutes)

            return SuccessResponse(
                success=True,
                data=template_data,
                message=f"Template download URL generated for {source_system_type}"
            )

        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning("Invalid template request", 
                           error=str(e), 
                           source_system_type=source_system_type)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error("Unexpected error getting template download URL", 
                          error=str(e), 
                          source_system_type=source_system_type)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_error_response(message="Failed to generate template download URL").model_dump(),
            )

    async def get_document_rows_download_url(
        self,
        request: Request,
        document_id: int,
        bulk_upload_use_cases: BulkUploadUseCasesDep
    ) -> SuccessResponse[TemplateDownloadResponse]:
        """Get download URL for document rows Excel export."""
        try:
            # Get user from middleware
            user: User = request.state.user

            # Validate specific DB permissions
            # await check_db_permissions_simple(user, [Roles.ACCESS_BULK_UPLOAD_AGREEMENTS])

            self.log_info("Getting document rows download URL", 
                         document_id=document_id,
                         user_email=user.email)

            # Validate document ID
            if document_id <= 0:
                raise ValueError("Document ID must be greater than 0")

            # Get document rows export data
            export_data = await bulk_upload_use_cases.get_document_rows_download_url(document_id, user)

            self.log_info("Document rows export URL generated successfully", 
                         document_id=document_id,
                         template_name=export_data.template_name,
                         expires_in_minutes=export_data.expires_in_minutes)

            return SuccessResponse(
                success=True,
                data=export_data,
                message=f"Document {document_id} rows export URL generated successfully"
            )

        except HTTPException:
            raise
        except ValueError as e:
            self.log_warning("Invalid document rows export request", 
                           error=str(e), 
                           document_id=document_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(message=str(e)).model_dump(),
            )
        except Exception as e:
            self.log_error("Unexpected error getting document rows export URL", 
                          error=str(e), 
                          document_id=document_id)
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(message=str(e)).model_dump(),
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=create_error_response(message="Failed to generate document rows export URL").model_dump(),
                )
# Controller instance (global)
bulk_upload_controller = AgreementsBulkUploadController()

# Endpoints that call the class
@router.post(
    "/bulk-upload",
    response_model=SuccessResponse[BulkUploadProcessResponse],
    summary="Upload bulk agreements Excel file",
    description="Upload and process an Excel file containing multiple agreements for bulk creation"
)
async def upload_bulk_agreements(
    request: Request,
    bulk_upload_use_cases: BulkUploadUseCasesDep,
    file: UploadFile = File(..., description="Excel file containing agreements data"),
    source_system_type: str = Form(..., description="Source system type")
) -> SuccessResponse[BulkUploadProcessResponse]:
    """Upload and process Excel file for bulk agreements creation."""
    return await bulk_upload_controller.upload_bulk_agreements(
        request=request,
        file=file,
        source_system_type=source_system_type,
        bulk_upload_use_cases=bulk_upload_use_cases
    )


@router.get(
    "/documents/{document_id}",
    response_model=SuccessResponse[BulkUploadDocumentResponse],
    summary="Get bulk upload document",
    description="Retrieve information about a specific bulk upload document"
)
async def get_bulk_upload_document(
    request: Request,
    document_id: int,
    bulk_upload_use_cases: BulkUploadUseCasesDep
) -> SuccessResponse[BulkUploadDocumentResponse]:
    """Get bulk upload document information by ID."""
    return await bulk_upload_controller.get_bulk_upload_document(
        request=request,
        document_id=document_id,
        bulk_upload_use_cases=bulk_upload_use_cases
    )


@router.post(
    "/documents/{document_id}/resolve",
    response_model=SuccessResponse[BulkUploadDocumentResolutionResponse],
    summary="Resolve bulk upload document",
    description="Process and resolve all rows in a bulk upload document to create agreements"
)
async def resolve_bulk_upload_document(
    request: Request,
    document_id: int,
    bulk_upload_use_cases: BulkUploadUseCasesDep
) -> SuccessResponse[BulkUploadDocumentResolutionResponse]:
    """Resolve bulk upload document by processing all rows and creating agreements."""
    return await bulk_upload_controller.resolve_bulk_upload_document(
        request=request,
        document_id=document_id,
        bulk_upload_use_cases=bulk_upload_use_cases
    )


@router.get(
    "/templates/{source_system_type}/download",
    response_model=SuccessResponse[TemplateDownloadResponse],
    summary="Get template download URL",
    description="Get download URL for bulk upload Excel template (SPF or PMM)"
)
async def get_template_download_url(
    request: Request,
    source_system_type: str,
    bulk_upload_use_cases: BulkUploadUseCasesDep
) -> SuccessResponse[TemplateDownloadResponse]:
    """Get download URL for bulk upload template."""
    return await bulk_upload_controller.get_template_download_url(
        request=request,
        source_system_type=source_system_type,
        bulk_upload_use_cases=bulk_upload_use_cases
    )


@router.get(
    "/documents/{document_id}/rows/download",
    response_model=SuccessResponse[TemplateDownloadResponse],
    summary="Get document rows download URL",
    description="Generate Excel export of document rows with observations and return download URL"
)
async def get_document_rows_download_url(
    request: Request,
    document_id: int,
    bulk_upload_use_cases: BulkUploadUseCasesDep
) -> SuccessResponse[TemplateDownloadResponse]:
    """Get download URL for document rows Excel export."""
    return await bulk_upload_controller.get_document_rows_download_url(
        request=request,
        document_id=document_id,
        bulk_upload_use_cases=bulk_upload_use_cases
    )
