"""Tests for logging module."""
import logging

from app.logging import JsonFormatter, PIIRedactingFormatter, RequestIDFilter, setup_logging


class TestPIIRedactingFormatter:
    def test_redacts_sensitive_fields(self):
        formatter = PIIRedactingFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg={"password": "secret123", "token": "abc123", "name": "john"},
            args=None,
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "secret123" not in formatted
        assert "abc123" not in formatted
        assert "john" in formatted


class TestRequestIDFilter:
    def test_filter_adds_request_id(self):
        filter_obj = RequestIDFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=None,
            exc_info=None,
        )
        assert filter_obj.filter(record) is True
        assert record.request_id == "-"

    def test_filter_preserves_existing_request_id(self):
        filter_obj = RequestIDFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=None,
            exc_info=None,
        )
        record.request_id = "abc-123"
        assert filter_obj.filter(record) is True
        assert record.request_id == "abc-123"


class TestSetupLogging:
    def test_setup_logging_idempotent(self):
        setup_logging()
        setup_logging()  # should not raise

    def test_json_formatter_includes_level_and_logger(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="my.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="something broke",
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        assert "my.logger" in output
        assert "ERROR" in output
        assert "something broke" in output
