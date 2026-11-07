import uuid

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging import get_logger
from app.security.rate_limit import check_rate_limit

logger = get_logger("app.middleware")


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append([b"x-request-id", request_id.encode()])
            await send(message)

        await self.app(scope, receive, send_wrapper)
        # store request id on a tokenvar-like is not needed; attach to logger via extra in route handlers


class RateLimitMiddleware:
    def __init__(self, app, default_limit: int | None = None, auth_limit: int | None = None):
        self.app = app
        self.default_limit = default_limit or settings.RATE_LIMIT_DEFAULT
        self.auth_limit = auth_limit or settings.RATE_LIMIT_AUTH

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path
        client = request.client.host if request.client else "unknown"
        is_auth = path.startswith("/auth/")

        key = f"{client}:{path}"
        limit = self.auth_limit if is_auth else self.default_limit

        if not check_rate_limit(key, limit):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded", "code": "rate_limited"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
