"""Exception handlers for standardized error responses."""

import traceback
from typing import Any, Dict, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import ErrorResponse, create_error_response
from app.core.logging import LoggerMixin


class ErrorHandlerManager(LoggerMixin):
    """Manager for error handling with logging capabilities."""
    
    def handle_validation_error(
        self, 
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        try:
            # Extract validation error details
            validation_errors = []
            for error in exc.errors():
                validation_error = {
                    "field": error["loc"][-1] if error["loc"] else "unknown",
                    "message": error["msg"],
                    "type": error["type"],
                    "input_value": str(error.get("input", "N/A"))[:100]  # Limit input value length
                }
                validation_errors.append(validation_error)
            
            # Create error response
            error_response = create_error_response(
                message="Validation error"
            )
            
            # Add validation details to data field
            error_response.data = {
                "validation_errors": validation_errors
            }
            
            # Log validation error
            self.log_warning(
                "Request validation failed",
                path=request.url.path,
                method=request.method,
                client_ip=self._get_client_ip(request),
                validation_errors_count=len(validation_errors),
                validation_errors=validation_errors
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response.model_dump()
            )
            
        except Exception as e:
            self.log_error(
                "Error in validation error handler", 
                error=e,
                original_exception=str(exc)
            )
            # Fallback response
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"message": "Validation error", "detail": str(exc)}
            )
    
    def handle_http_exception(
        self, 
        request: Request, 
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        try:
            # Handle detail - if it's already a dict, use it directly
            if isinstance(exc.detail, dict):
                return JSONResponse(
                    status_code=exc.status_code,
                    content=exc.detail
                )
            
            # Create error response for string details
            error_response = create_error_response(
                message=exc.detail if exc.detail else "HTTP error occurred"
            )
            
            # Log HTTP exception
            self.log_warning(
                "HTTP exception occurred",
                path=request.url.path,
                method=request.method,
                status_code=exc.status_code,
                client_ip=self._get_client_ip(request),
                detail=exc.detail
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response.model_dump()
            )
            
        except Exception as e:
            self.log_error(
                "Error in HTTP exception handler", 
                error=e,
                original_exception=str(exc)
            )
            # Fallback response
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": "HTTP error occurred"}
            )
    
    def handle_general_exception(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions."""
        try:
            # Create error response
            error_response = create_error_response(
                message="Internal server error"
            )
            
            # Get exception details
            exception_type = type(exc).__name__
            exception_message = str(exc)
            traceback_str = traceback.format_exc()
            
            # Log general exception
            self.log_error(
                "Unhandled exception occurred",
                path=request.url.path,
                method=request.method,
                client_ip=self._get_client_ip(request),
                exception_type=exception_type,
                exception_message=exception_message,
                traceback=traceback_str
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.model_dump()
            )
            
        except Exception as e:
            self.log_error(
                "Error in general exception handler", 
                error=e,
                original_exception=str(exc)
            )
            # Fallback response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


# Global error handler manager instance
_error_handler_manager = ErrorHandlerManager()


# Exception handler functions for FastAPI
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return _error_handler_manager.handle_validation_error(request, exc)


async def http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    return _error_handler_manager.handle_http_exception(request, exc)


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    return _error_handler_manager.handle_general_exception(request, exc)


# Convenience functions for direct usage
def handle_validation_error_directly(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation error directly (for testing or manual usage)."""
    return _error_handler_manager.handle_validation_error(request, exc)


def handle_http_exception_directly(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exception directly (for testing or manual usage)."""
    return _error_handler_manager.handle_http_exception(request, exc)


def handle_general_exception_directly(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle general exception directly (for testing or manual usage)."""
    return _error_handler_manager.handle_general_exception(request, exc)
