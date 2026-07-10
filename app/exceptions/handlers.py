"""Global FastAPI exception handlers.

Registered on the ``FastAPI`` app instance in ``app.main``, these
handlers translate internal exceptions into consistent, well-formed
JSON error responses and the correct HTTP status codes.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.custom_exception import (
    AppException,
    BadRequestException,
    NotFoundException,
    ValidationException,
)

logger = logging.getLogger("retail_discount_engine")


def _error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    """Build a consistent error response body.

    Args:
        status_code: HTTP status code to return.
        error_code: Machine-readable error code.
        message: Human-readable error message.

    Returns:
        JSONResponse: A uniformly-shaped error payload.
    """

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(NotFoundException)
    async def handle_not_found(request: Request, exc: NotFoundException) -> JSONResponse:
        return _error_response(status.HTTP_404_NOT_FOUND, exc.error_code.value, exc.message)

    @app.exception_handler(BadRequestException)
    async def handle_bad_request(request: Request, exc: BadRequestException) -> JSONResponse:
        return _error_response(status.HTTP_400_BAD_REQUEST, exc.error_code.value, exc.message)

    @app.exception_handler(ValidationException)
    async def handle_validation(request: Request, exc: ValidationException) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY, exc.error_code.value, exc.message
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # This catches Pydantic schema validation failures raised by
        # FastAPI itself (e.g. malformed request bodies).
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            str(exc.errors()),
        )

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        # Fallback for any AppException subclass not explicitly handled
        # above (defensive; keeps behavior correct as new exception
        # types are added).
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, exc.error_code.value, exc.message
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        # Catch-all: never leak stack traces to the client, but log
        # them server-side for debugging.
        logger.exception("Unhandled exception while processing request %s", request.url)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
        )
