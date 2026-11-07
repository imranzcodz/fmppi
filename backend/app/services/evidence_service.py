from app.config import settings


def validate_upload_file(file) -> None:
    """Validate uploaded file type and size against settings limits."""
    content_type = file.content_type or ""
    allowed = [t.strip() for t in settings.ALLOWED_IMAGE_MIME_TYPES.split(",") if t.strip()]
    if content_type not in allowed:
        raise ValueError(f"Unsupported file type: {content_type}. Allowed: {', '.join(allowed)}")

    # size: read into memory to enforce limit
    contents = file.file.read()
    file.file.seek(0)
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise ValueError(f"File too large: {len(contents)} bytes. Max: {settings.MAX_UPLOAD_SIZE} bytes")
    if not contents:
        raise ValueError("Empty file")
    return contents
