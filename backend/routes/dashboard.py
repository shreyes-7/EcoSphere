"""Dashboard REST APIs for overall platform analytics and building KPI summaries."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import ClosedLoopRun, OptimizationHistory, Simulation
from backend.schemas.api_schemas import DashboardSummaryResponse
from backend.utils.logger import get_logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = get_logger(__name__)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get overall building optimization dashboard summary",
)
def get_dashboard_summary(
    database_session: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    """Compute and return top-level building performance analytics and optimization KPIs."""
    total_sims = database_session.query(Simulation).count()
    completed_sims = database_session.query(Simulation).filter_by(status="completed").count()
    total_runs = database_session.query(ClosedLoopRun).count()

    opt_records = database_session.query(OptimizationHistory).all()

    total_saved_kwh = 0.0
    savings_percents: list[float] = []

    for rec in opt_records:
        if rec.energy_before is not None and rec.energy_after is not None:
            saved = max(rec.energy_before - rec.energy_after, 0.0)
            total_saved_kwh += saved
        if rec.actual_savings is not None:
            savings_percents.append(rec.actual_savings)

    avg_savings_pct = (
        round(sum(savings_percents) / len(savings_percents), 2)
        if savings_percents
        else 0.0
    )

    latest_rec = database_session.query(OptimizationHistory).order_by(desc(OptimizationHistory.timestamp)).first()
    latest_recommendation = latest_rec.final_recommendation if latest_rec else None

    logger.info(
        "API GET /dashboard/summary: total_sims=%s total_runs=%s total_saved=%.2f kWh",
        total_sims,
        total_runs,
        total_saved_kwh,
    )

    return DashboardSummaryResponse(
        total_simulations=total_sims,
        completed_simulations=completed_sims,
        total_closed_loop_runs=total_runs,
        total_energy_saved_kwh=round(total_saved_kwh, 2),
        average_savings_percent=avg_savings_pct,
        active_agents=4,
        latest_recommendation=latest_recommendation,
    )
