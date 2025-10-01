"""Standard response schemas for all API endpoints."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful")
    message: str = Field(..., description="Human-readable message about the operation")


class SuccessResponse(BaseResponse, Generic[T]):
    success: bool = Field(True, description="Always true for successful operations")
    data: T = Field(..., description="The actual response data")
    message: str = Field(default="Operation completed successfully", description="Success message")


class ErrorResponse(BaseResponse):
    success: bool = Field(False, description="Always false for error operations")
    data: Optional[Any] = Field(None, description="Always null for errors")
    message: str = Field(..., description="Error description")


class PaginatedResponse(BaseResponse, Generic[T]):
    success: bool = Field(True, description="Always true for successful operations")
    data: T = Field(..., description="The paginated data")
    message: str = Field(default="Data retrieved successfully", description="Success message")
    pagination: dict = Field(..., description="Pagination information")


# Convenience functions for creating responses
def create_success_response(data: Any, message: str = "Operation completed successfully") -> SuccessResponse:
    return SuccessResponse(data=data, message=message)


def create_error_response(message: str) -> ErrorResponse:
    return ErrorResponse(message=message)


def create_paginated_response(data: Any, pagination: dict, message: str = "Data retrieved successfully") -> PaginatedResponse:
    return PaginatedResponse(data=data, message=message, pagination=pagination)
