"""Optimization REST APIs for triggering and querying building optimization sessions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.config import Settings, get_settings
from backend.database.database import get_db
from backend.database.models import ClosedLoopRun, OptimizationHistory, Simulation
from backend.schemas.api_schemas import (
    ClosedLoopStatusResponse,
    OptimizationHistoryItem,
    OptimizationHistoryListResponse,
    SimulationCompareResponse,
    SimulationMetricsDetail,
    StartOptimizationRequest,
)
from backend.schemas.closed_loop_schemas import ClosedLoopConfig, ClosedLoopResult
from backend.schemas.explainability_schemas import OptimizationExplanationResponse
from backend.services.agents.supervisor_agent import create_default_supervisor
from backend.services.closed_loop_service import ClosedLoopService
from backend.services.explainability_service import ExplainabilityService
from backend.services.idf_modifier import IDFModifierService
from backend.services.optimization_engine import OptimizationEngine
from backend.services.optimization_repository import OptimizationRepository
from backend.utils.exceptions import EcoSphereError
from backend.utils.logger import get_logger

router = APIRouter(prefix="/optimize", tags=["Optimization"])
logger = get_logger(__name__)


@router.post(
    "/start",
    response_model=ClosedLoopResult,
    status_code=status.HTTP_200_OK,
    summary="Start autonomous closed-loop building optimization",
)
def start_optimization(
    payload: StartOptimizationRequest,
    database_session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ClosedLoopResult:
    """Trigger an autonomous closed-loop optimization session for a completed simulation."""
    try:
        repo = OptimizationRepository(database_session)
        supervisor = create_default_supervisor(settings)
        engine = OptimizationEngine(repository=repo, supervisor=supervisor)
        idf_modifier = IDFModifierService(settings)

        closed_loop_service = ClosedLoopService(
            settings=settings,
            repository=repo,
            engine=engine,
            idf_modifier=idf_modifier,
        )

        config = ClosedLoopConfig(
            max_iterations=payload.max_iterations,
            target_reduction_percent=payload.target_reduction_percent,
            min_improvement_threshold_percent=payload.min_improvement_threshold_percent,
        )

        logger.info(
            "API POST /optimize/start called: simulation_id=%s max_iter=%s target=%.1f%%",
            payload.simulation_id,
            payload.max_iterations,
            payload.target_reduction_percent,
        )
        return closed_loop_service.run_closed_loop(
            simulation_id=payload.simulation_id,
            config=config,
        )
    except EcoSphereError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get(
    "/status/{closed_loop_run_id}",
    response_model=ClosedLoopStatusResponse,
    summary="Get closed-loop optimization run status",
)
def get_optimization_status(
    closed_loop_run_id: int,
    database_session: Session = Depends(get_db),
) -> ClosedLoopStatusResponse:
    """Return the current state and metadata for a closed-loop run session."""
    run = database_session.get(ClosedLoopRun, closed_loop_run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Closed-loop run not found: {closed_loop_run_id}",
        )

    return ClosedLoopStatusResponse(
        closed_loop_run_id=run.id,
        simulation_id=run.simulation_id,
        status=run.status,
        max_iterations=run.max_iterations,
        current_iteration=run.current_iteration,
        total_energy_saved=run.total_energy_saved,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get(
    "/history",
    response_model=OptimizationHistoryListResponse,
    summary="Get optimization history records",
)
def get_optimization_history(
    simulation_id: int | None = Query(None, description="Optional simulation ID filter"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    database_session: Session = Depends(get_db),
) -> OptimizationHistoryListResponse:
    """Return historical optimization decisions filtered optionally by simulation ID."""
    query = database_session.query(OptimizationHistory)
    if simulation_id is not None:
        query = query.filter_by(simulation_id=simulation_id)

    total_count = query.count()
    records = query.order_by(desc(OptimizationHistory.timestamp)).limit(limit).all()

    history_items = [
        OptimizationHistoryItem(
            id=rec.id,
            simulation_id=rec.simulation_id,
            closed_loop_run_id=rec.closed_loop_run_id,
            iteration=rec.iteration,
            energy_before=rec.energy_before,
            energy_after=rec.energy_after,
            expected_savings=rec.expected_savings,
            actual_savings=rec.actual_savings,
            final_recommendation=rec.final_recommendation,
            timestamp=rec.timestamp,
        )
        for rec in records
    ]

    return OptimizationHistoryListResponse(
        total_count=total_count,
        history=history_items,
    )


@router.get(
    "/explanation/{optimization_id}",
    response_model=OptimizationExplanationResponse,
    summary="Get explainable AI report for an optimization decision",
)
def get_optimization_explanation(
    optimization_id: int,
    database_session: Session = Depends(get_db),
) -> OptimizationExplanationResponse:
    """Return a detailed explainability report for a specific optimization ID."""
    try:
        repo = OptimizationRepository(database_session)
        service = ExplainabilityService(repo)
        return service.get_explanation_by_optimization_id(optimization_id)
    except EcoSphereError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get(
    "/compare",
    response_model=SimulationCompareResponse,
    summary="Compare energy metrics between two simulation runs",
)
def compare_simulations(
    simulation_id_1: int = Query(..., description="First simulation ID (baseline)"),
    simulation_id_2: int = Query(..., description="Second simulation ID (modified)"),
    database_session: Session = Depends(get_db),
) -> SimulationCompareResponse:
    """Compare energy performance and calculate savings between two simulation runs."""
    sim1 = database_session.get(Simulation, simulation_id_1)
    sim2 = database_session.get(Simulation, simulation_id_2)

    if sim1 is None or sim2 is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both simulations not found: {simulation_id_1}, {simulation_id_2}",
        )

    e1 = sim1.electricity if sim1.electricity is not None else (sim1.total_energy or 0.0)
    e2 = sim2.electricity if sim2.electricity is not None else (sim2.total_energy or 0.0)

    energy_saved = round(e1 - e2, 2)
    savings_percent = round(((e1 - e2) / e1 * 100.0), 2) if e1 > 0 else 0.0

    return SimulationCompareResponse(
        simulation_1=SimulationMetricsDetail(
            id=sim1.id,
            building_name=sim1.building_name,
            total_energy=sim1.total_energy,
            electricity=sim1.electricity,
            cooling=sim1.cooling,
            heating=sim1.heating,
            hvac=sim1.hvac,
        ),
        simulation_2=SimulationMetricsDetail(
            id=sim2.id,
            building_name=sim2.building_name,
            total_energy=sim2.total_energy,
            electricity=sim2.electricity,
            cooling=sim2.cooling,
            heating=sim2.heating,
            hvac=sim2.hvac,
        ),
        energy_saved=energy_saved,
        savings_percent=savings_percent,
    )
