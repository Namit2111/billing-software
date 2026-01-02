"""
Common schema types
"""
from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel
from datetime import datetime


DataT = TypeVar('DataT')


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success response wrapper"""
    success: bool = True
    data: DataT
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: dict


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = 1
    per_page: int = 20
    total: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated list response"""
    success: bool = True
    data: List[DataT]
    meta: PaginationMeta


class DeleteResponse(BaseModel):
    """Delete operation response"""
    success: bool = True
    message: str = "Resource deleted successfully"


class MessageResponse(BaseModel):
    """Simple message response"""
    success: bool = True
    message: str

