"""
Exception handlers and custom exceptions
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import traceback

from app.core.config import settings


class BillFlowException(Exception):
    """Base exception for BillFlow application"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(BillFlowException):
    """Resource not found exception"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class UnauthorizedError(BillFlowException):
    """Authentication required exception"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenError(BillFlowException):
    """Access denied exception"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class ValidationError(BillFlowException):
    """Validation error exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")


class ConflictError(BillFlowException):
    """Resource conflict exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code="CONFLICT")


class BadRequestError(BillFlowException):
    """Bad request exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_code="BAD_REQUEST")


class InvoiceError(BillFlowException):
    """Invoice-specific exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_code="INVOICE_ERROR")


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the application"""
    
    @app.exception_handler(BillFlowException)
    async def billflow_exception_handler(request: Request, exc: BillFlowException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message
                }
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": exc.errors() if hasattr(exc, 'errors') else str(exc)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Log the full error in development
        if settings.DEBUG:
            traceback.print_exc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred" if not settings.DEBUG else str(exc)
                }
            }
        )

