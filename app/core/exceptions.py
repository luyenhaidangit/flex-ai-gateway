# app/core/exceptions.py


class AppBaseException(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppBaseException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", id: int | str | None = None):
        detail = f"{resource} not found" if id is None else f"{resource} with id '{id}' not found"
        super().__init__(detail)


class ServiceUnavailableError(AppBaseException):
    """Raised when a downstream service (DB, ML model, etc.) is not available."""

    def __init__(self, service: str = "Service"):
        super().__init__(f"{service} is currently unavailable.")


class ConflictError(AppBaseException):
    """Raised when there is a data conflict (e.g., duplicate record)."""

    def __init__(self, message: str = "Conflict: resource already exists."):
        super().__init__(message)


class BadRequestError(AppBaseException):
    """Raised when the client sends an invalid request."""

    def __init__(self, message: str = "Bad request."):
        super().__init__(message)


class UnauthorizedError(AppBaseException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized: invalid credentials."):
        super().__init__(message)


class ConfigurationError(AppBaseException):
    """Raised when the application configuration is invalid."""

    def __init__(self, message: str = "Invalid application configuration."):
        super().__init__(message)
