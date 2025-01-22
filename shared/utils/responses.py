"""
Centralized response handling for consistent API responses
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any


class APIResponse:
    @staticmethod
    def success(message: str, data: Any = None, status_code: int = 200) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data
            }
        )

    @staticmethod
    def error(message: str, data: Any = None, status_code: int = 400) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "data": data
            }
        )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error["loc"][-1] if error["loc"] else None,
            "message": error["msg"]
        })

    return APIResponse.error(
        message="Request Validation error",
        data=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return APIResponse.error(
        message=exc.detail,
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    return APIResponse.error(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
