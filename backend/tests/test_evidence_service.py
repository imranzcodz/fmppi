"""Tests for evidence service."""
from unittest.mock import MagicMock

from app.services.evidence_service import validate_upload_file


class TestValidateUploadFile:
    def test_allows_jpeg(self):
        file = MagicMock()
        file.content_type = "image/jpeg"
        file.file.read.return_value = b"\x89PNG fake"
        result = validate_upload_file(file)
        assert result == b"\x89PNG fake"

    def test_rejects_pdf(self):
        file = MagicMock()
        file.content_type = "application/pdf"
        file.file.read.return_value = b"%PDF fake"
        try:
            validate_upload_file(file)
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Unsupported file type" in str(exc)

    def test_rejects_empty_file(self):
        file = MagicMock()
        file.content_type = "image/jpeg"
        file.file.read.return_value = b""
        try:
            validate_upload_file(file)
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Empty file" in str(exc)
