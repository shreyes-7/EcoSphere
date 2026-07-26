"""System telemetry and structured log search REST APIs."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from backend.schemas.monitoring_schemas import LogSearchResponse, SystemMetricsResponse
from backend.services.monitoring_service import MonitoringService
from backend.utils.logger import get_logger

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = get_logger(__name__)


@router.get(
    "/logs",
    response_model=LogSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search and filter structured agent execution logs",
)
def search_agent_logs(
    agent: str | None = Query(None, description="Filter by agent name (energy, comfort, cost, sustainability, supervisor)"),
    level: str | None = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    query: str | None = Query(None, description="Search text in recommendation or reason"),
    limit: int = Query(50, ge=1, le=500, description="Maximum log entries to return"),
) -> LogSearchResponse:
    """Return searchable structured log entries filtered by agent, log level, or query string."""
    return MonitoringService.search_logs(
        agent=agent,
        level=level,
        query=query,
        limit=limit,
    )


@router.get(
    "/metrics",
    response_model=SystemMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get top-level system telemetry and agent latency metrics",
)
def get_system_telemetry() -> SystemMetricsResponse:
    """Return agent execution latency breakdown, evaluation counts, and system metrics."""
    return MonitoringService.get_system_metrics()


@router.post(
    "/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear all structured in-memory telemetry logs",
)
def clear_telemetry_logs() -> dict[str, str]:
    """Purge in-memory telemetry log entries and reset counters."""
    MonitoringService.clear_logs()
    return {"message": "All structured telemetry logs cleared successfully."}
