"""FastAPI application entrypoint for EcoSphere."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import Settings, get_settings
from backend.database.database import initialize_database
from backend.database import models as database_models  # noqa: F401
from backend.models.response_models import HealthResponse
from backend.routes import ai, simulation
from backend.utils.exceptions import EcoSphereError
from backend.utils.logger import configure_logging, get_logger


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize database tables and application logging on startup."""
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)
    initialize_database()
    logger.info("EcoSphere API started")
    yield
    logger.info("EcoSphere API stopped")


def create_application(settings: Settings | None = None) -> FastAPI:
    """Create the configured FastAPI application."""
    application_settings = settings or get_settings()
    application = FastAPI(
        title=application_settings.app_name,
        version=application_settings.app_version,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def request_logging_and_timing(request: Request, call_next: object) -> JSONResponse:
        """Log each request and attach a processing-time response header."""
        started_at = time.perf_counter()
        logger = get_logger("backend.request")
        try:
            response = await call_next(request)  # type: ignore[operator]
        except Exception:
            logger.exception("Unhandled request error: %s %s", request.method, request.url.path)
            raise
        duration_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        logger.info("%s %s -> %s (%.2f ms)", request.method, request.url.path, response.status_code, duration_ms)
        return response

    @application.exception_handler(EcoSphereError)
    async def domain_exception_handler(_: Request, error: EcoSphereError) -> JSONResponse:
        """Return expected domain failures as structured bad requests."""
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, error: RequestValidationError) -> JSONResponse:
        """Return Pydantic failures in the standard API response shape."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": error.errors()},
        )

    @application.get("/", response_model=HealthResponse, tags=["System"])
    async def root() -> HealthResponse:
        """Return application identity and runtime status."""
        return HealthResponse(
            status="running",
            app=application_settings.app_name,
            version=application_settings.app_version,
        )

    @application.get("/health", response_model=HealthResponse, tags=["System"])
    async def health() -> HealthResponse:
        """Return the API health status."""
        return HealthResponse(
            status="running",
            app=application_settings.app_name,
            version=application_settings.app_version,
        )

    application.include_router(ai.router)
    application.include_router(simulation.router)
    return application


app = create_application()
