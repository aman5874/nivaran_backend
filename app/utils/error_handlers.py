import logging
from typing import Callable, Dict, Any, Union
from fastapi import Request, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import openai

from app.models.response_models import ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors with status code and detail"""
    def __init__(self, status_code: int, message: str, details: Dict[str, Any] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(message)

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the FastAPI app"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """Handle custom API errors"""
        logger.error(f"API Error: {exc.message}, details: {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=True,
                message=exc.message,
                details=exc.details
            ).model_dump()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=True,
                message=str(exc.detail)
            ).model_dump()
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors"""
        details = {err["loc"][-1]: err["msg"] for err in exc.errors()}
        logger.error(f"Validation Error: {details}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=True,
                message="Validation error",
                details=details
            ).model_dump()
        )
    
    @app.exception_handler(openai.OpenAIError)
    async def openai_error_handler(request: Request, exc: openai.OpenAIError) -> JSONResponse:
        """Handle OpenAI API errors"""
        logger.error(f"OpenAI API Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=ErrorResponse(
                error=True,
                message=f"OpenAI API error: {str(exc)}"
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions"""
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=True,
                message="Internal server error"
            ).model_dump()
        ) 