import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.editor import router as editor_router
from app.api.v1.problems import router as problems_router
from app.api.v1.scoring import internal_router as internal_scoring_router
from app.api.v1.scoring import router as scoring_router
from app.api.v1.students import router as students_router
from app.api.v1.submissions import router as submissions_router
from app.core.config import settings
from app.middlewares.auth_middleware import AuthRateLimitMiddleware
from app.middlewares.exception_handler import global_exception_handler
from app.middlewares.http_exception_handler import (
    http_exception_handler,
    validation_exception_handler,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Elite Internship Hackathon Platform API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthRateLimitMiddleware)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(students_router, prefix=settings.api_v1_prefix)
app.include_router(problems_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(editor_router, prefix=settings.api_v1_prefix)
app.include_router(submissions_router, prefix=settings.api_v1_prefix)
app.include_router(scoring_router, prefix=settings.api_v1_prefix)
app.include_router(internal_scoring_router, prefix=settings.api_v1_prefix)
app.include_router(dashboard_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def root_health_check() -> dict:
    """Unprefixed health check for container/orchestrator probes."""
    return {"success": True, "message": "ok", "data": {"status": "healthy"}, "errors": None}
