"""Historical analytics and downloadable report export REST APIs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.analytics_schemas import ClosedLoopAnalyticsResponse
from backend.services.analytics_service import AnalyticsService
from backend.utils.exceptions import EcoSphereError
from backend.utils.logger import get_logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger(__name__)


@router.get(
    "/run/{closed_loop_run_id}",
    response_model=ClosedLoopAnalyticsResponse,
    summary="Get multi-iteration historical trend progression",
)
def get_run_analytics(
    closed_loop_run_id: int,
    database_session: Session = Depends(get_db),
) -> ClosedLoopAnalyticsResponse:
    """Compute and return multi-step metrics progression across Energy, PMV, Carbon, Cost, and HVAC demand."""
    try:
        service = AnalyticsService(database_session)
        return service.get_run_analytics(closed_loop_run_id)
    except EcoSphereError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error


@router.get(
    "/export/csv/{closed_loop_run_id}",
    summary="Export closed-loop run analytics as CSV report",
)
def export_csv_report(
    closed_loop_run_id: int,
    database_session: Session = Depends(get_db),
) -> Response:
    """Generate and download a CSV analytics report for a closed-loop run session."""
    try:
        service = AnalyticsService(database_session)
        csv_content = service.export_csv_report(closed_loop_run_id)
        filename = f"ecosphere_run_{closed_loop_run_id:06d}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except EcoSphereError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error


@router.get(
    "/export/json/{closed_loop_run_id}",
    summary="Export closed-loop run analytics as JSON report",
)
def export_json_report(
    closed_loop_run_id: int,
    database_session: Session = Depends(get_db),
) -> Response:
    """Generate and download a JSON analytics report for a closed-loop run session."""
    try:
        service = AnalyticsService(database_session)
        json_content = service.export_json_report(closed_loop_run_id)
        filename = f"ecosphere_run_{closed_loop_run_id:06d}.json"
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except EcoSphereError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error


@router.get(
    "/export/markdown/{closed_loop_run_id}",
    summary="Export closed-loop run analytics as Markdown report",
)
def export_markdown_report(
    closed_loop_run_id: int,
    database_session: Session = Depends(get_db),
) -> Response:
    """Generate and download a Markdown analytics report for a closed-loop run session."""
    try:
        service = AnalyticsService(database_session)
        md_content = service.export_markdown_report(closed_loop_run_id)
        filename = f"ecosphere_run_{closed_loop_run_id:06d}.md"
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except EcoSphereError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
