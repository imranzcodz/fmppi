from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import audit, auth, cases, ml, reporter, users, verify
from app.config import settings
from app.database import init_db
from app.exceptions import AppError
from app.logging import setup_logging
from app.middleware import RateLimitMiddleware, RequestIDMiddleware

setup_logging()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS allowlist
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware: request ID tracing + rate limiting
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message, "code": exc.code})


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reporter.router)
app.include_router(cases.router)
app.include_router(verify.router)
app.include_router(ml.router)
app.include_router(audit.router)
