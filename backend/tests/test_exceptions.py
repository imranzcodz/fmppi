"""Tests for exceptions module."""
from app.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class TestAppError:
    def test_defaults(self):
        err = AppError("something went wrong")
        assert err.message == "something went wrong"
        assert err.status_code == 400
        assert err.code == "app_error"

    def test_custom_values(self):
        err = AppError("custom", status_code=500, code="custom_code")
        assert err.message == "custom"
        assert err.status_code == 500
        assert err.code == "custom_code"


class TestNotFoundError:
    def test_defaults(self):
        err = NotFoundError()
        assert err.status_code == 404
        assert err.code == "not_found"

    def test_custom_message(self):
        err = NotFoundError("Case not found")
        assert err.message == "Case not found"


class TestConflictError:
    def test_defaults(self):
        err = ConflictError()
        assert err.status_code == 409
        assert err.code == "conflict"


class TestForbiddenError:
    def test_defaults(self):
        err = ForbiddenError()
        assert err.status_code == 403
        assert err.code == "forbidden"


class TestUnauthorizedError:
    def test_defaults(self):
        err = UnauthorizedError()
        assert err.status_code == 401
        assert err.code == "unauthorized"


class TestValidationError:
    def test_defaults(self):
        err = ValidationError()
        assert err.status_code == 400
        assert err.code == "validation_error"
