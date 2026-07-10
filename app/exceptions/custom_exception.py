"""Custom application exceptions.

Using dedicated exception classes (instead of raising HTTPException
directly from the service/repository layers) keeps those layers free
of any HTTP-specific concerns, honoring the Single Responsibility
Principle and Clean Architecture's dependency rule: inner layers
should not depend on outer, delivery-mechanism details.

The mapping from these exceptions to actual HTTP status codes happens
exclusively in ``app.exceptions.handlers``.
"""

from app.core.constants import ErrorCode


class AppException(Exception):
    """Base class for all application-specific exceptions.

    Attributes:
        message: Human-readable error description.
        error_code: Machine-readable error code from ``ErrorCode``.
    """

    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    error_code = ErrorCode.NOT_FOUND


class BadRequestException(AppException):
    """Raised when a request is well-formed but semantically invalid.

    Examples include violating a business rule such as "minimum
    purchase not met" or "quantity must be greater than zero".
    """

    error_code = ErrorCode.BAD_REQUEST


class ValidationException(AppException):
    """Raised for domain validation failures not caught by Pydantic.

    Typically used inside validators (``app.validators``) that need to
    check state against the database (e.g. "product is inactive"),
    which Pydantic's stateless schema validation cannot express.
    """

    error_code = ErrorCode.VALIDATION_ERROR


class DuplicateResourceException(BadRequestException):
    """Raised when attempting to create a resource that already exists.

    For example, registering a customer with an email that is already
    in use.
    """

    pass
