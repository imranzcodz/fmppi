from fastapi import status


class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, code: str | None = None):
        self.message = message
        self.status_code = status_code
        self.code = code or "app_error"
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND, "not_found")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT, "conflict")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN, "forbidden")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "unauthorized")


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, "validation_error")
