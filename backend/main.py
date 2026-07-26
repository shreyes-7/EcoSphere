"""FastAPI application entrypoint for EcoSphere."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config import Settings, get_settings
from backend.database import models as database_models  # noqa: F401
from backend.database.database import initialize_database
from backend.models.response_models import HealthResponse
from backend.routes import agents, ai, analytics, dashboard, digital_twin, facility_manager, monitoring, occupancy, optimize, playback, rl, self_healing, simulation, xai
from backend.utils.exceptions import EcoSphereError
from backend.utils.logger import configure_logging, get_logger


def verify_and_initialize_environment() -> list[Path]:
    """
    Verify and idempotently initialize all required project directories across platforms.
    Raises RuntimeError if directory creation fails.
    """
    project_root = Path(__file__).resolve().parent.parent
    required_directories = [
        project_root / "backend" / "database",
        project_root / "energyplus" / "output",
        project_root / "logs",
        project_root / "reports",
        project_root / "uploads",
        project_root / "uploads" / "idf",
        project_root / "uploads" / "weather",
        project_root / "simulation_output",
    ]

    for directory in required_directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as error:
            error_msg = f"Failed to initialize required environment directory '{directory}': {error}"
            print(f"CRITICAL: {error_msg}")
            raise RuntimeError(error_msg) from error

    return required_directories


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize environment directories, database tables, and application logging on startup."""
    verify_and_initialize_environment()

    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)

    logger.info("✓ Required directories verified/created successfully")

    initialize_database()
    logger.info("✓ SQLite database and SQLAlchemy tables initialized successfully")
    logger.info("✓ Application logger initialized successfully")
    logger.info("✓ EcoSphere project environment initialized successfully")

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

    @application.get("/dashboard", tags=["Dashboard"], include_in_schema=False)
    async def dashboard_redirect() -> RedirectResponse:
        """Redirect legacy dashboard path to static UI."""
        return RedirectResponse(url="/app/")

    application.include_router(ai.router)
    application.include_router(simulation.router)
    application.include_router(optimize.router)
    application.include_router(dashboard.router)
    application.include_router(agents.router)
    application.include_router(analytics.router)
    application.include_router(monitoring.router)
    application.include_router(digital_twin.router)
    application.include_router(occupancy.router)
    application.include_router(rl.router)
    application.include_router(xai.router)
    application.include_router(self_healing.router)
    application.include_router(facility_manager.router)
    application.include_router(playback.router)

    frontend_dist_dir = Path(__file__).parent.parent / "frontend" / "dist"
    static_dir = frontend_dist_dir if frontend_dist_dir.is_dir() else (Path(__file__).parent / "static")
    if static_dir.is_dir():
        application.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="static_app")

    return application


app = create_application()
