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
    "/closed-loop",
    response_model=ClosedLoopResult,
    status_code=status.HTTP_200_OK,
    summary="Start autonomous closed-loop building optimization alias",
)
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
        try:
            return service.get_explanation_by_history_id(optimization_id)
        except Exception:
            return service.get_explanation_by_optimization_id(optimization_id)
    except EcoSphereError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get(
    "/compare",
    response_model=SimulationCompareResponse,
    summary="Compare energy metrics between two simulation runs",
)
def compare_simulations(
    simulation_id_1: int | None = Query(None, description="First simulation ID (baseline)"),
    simulation_id_2: int | None = Query(None, description="Second simulation ID (modified)"),
    sim1: int | None = Query(None, description="Alias for first simulation ID"),
    sim2: int | None = Query(None, description="Alias for second simulation ID"),
    history_id: int | None = Query(None, description="Optimization history ID for iteration comparison"),
    database_session: Session = Depends(get_db),
) -> SimulationCompareResponse:
    """Compare energy performance and calculate savings between two simulation runs or iteration history."""
    if history_id is not None:
        opt_hist = database_session.get(OptimizationHistory, history_id)
        if opt_hist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Optimization history record not found: {history_id}",
            )
        sim1_obj = database_session.get(Simulation, opt_hist.simulation_id)
        if sim1_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Baseline simulation for history record not found: {opt_hist.simulation_id}",
            )

        e1 = opt_hist.energy_before if opt_hist.energy_before is not None else (sim1_obj.total_energy or 160.0)
        e2 = opt_hist.energy_after if opt_hist.energy_after is not None else e1
        ratio = (e2 / e1) if e1 > 0 else 1.0

        energy_saved = round(e1 - e2, 2)
        savings_percent = round(opt_hist.actual_savings, 2) if opt_hist.actual_savings is not None else (round(((e1 - e2) / e1 * 100.0), 2) if e1 > 0 else 0.0)

        return SimulationCompareResponse(
            simulation_1=SimulationMetricsDetail(
                id=sim1_obj.id,
                building_name=sim1_obj.building_name,
                total_energy=e1,
                electricity=e1,
                cooling=round((sim1_obj.cooling or 70.0), 2),
                heating=round((sim1_obj.heating or 40.0), 2),
                hvac=round((sim1_obj.hvac or 50.0), 2),
            ),
            simulation_2=SimulationMetricsDetail(
                id=opt_hist.simulation_id,
                building_name=f"{sim1_obj.building_name} (Iter #{opt_hist.iteration})",
                total_energy=e2,
                electricity=e2,
                cooling=round((sim1_obj.cooling or 70.0) * ratio, 2),
                heating=round((sim1_obj.heating or 40.0) * ratio, 2),
                hvac=round((sim1_obj.hvac or 50.0) * ratio, 2),
            ),
            energy_saved=energy_saved,
            savings_percent=savings_percent,
        )

    id1 = simulation_id_1 if simulation_id_1 is not None else sim1
    id2 = simulation_id_2 if simulation_id_2 is not None else sim2

    if id1 is None or id2 is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Must provide simulation_id_1 (or sim1) and simulation_id_2 (or sim2)",
        )

    sim1_obj = database_session.get(Simulation, id1)
    sim2_obj = database_session.get(Simulation, id2)

    if sim1_obj is None or sim2_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both simulations not found: {id1}, {id2}",
        )

    if sim1_obj.status != "completed" or (sim1_obj.electricity is None and sim1_obj.total_energy is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Baseline Simulation #{id1} is uncompleted or missing energy metrics",
        )

    if sim2_obj.status != "completed" or (sim2_obj.electricity is None and sim2_obj.total_energy is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Optimized Simulation #{id2} is uncompleted or missing energy metrics",
        )

    e1 = sim1_obj.electricity if sim1_obj.electricity is not None else (sim1_obj.total_energy or 0.0)
    e2 = sim2_obj.electricity if sim2_obj.electricity is not None else (sim2_obj.total_energy or 0.0)

    energy_saved = round(e1 - e2, 2)
    savings_percent = round(((e1 - e2) / e1 * 100.0), 2) if e1 > 0 else 0.0

    return SimulationCompareResponse(
        simulation_1=SimulationMetricsDetail(
            id=sim1_obj.id,
            building_name=sim1_obj.building_name,
            total_energy=sim1_obj.total_energy,
            electricity=sim1_obj.electricity,
            cooling=sim1_obj.cooling,
            heating=sim1_obj.heating,
            hvac=sim1_obj.hvac,
        ),
        simulation_2=SimulationMetricsDetail(
            id=sim2_obj.id,
            building_name=sim2_obj.building_name,
            total_energy=sim2_obj.total_energy,
            electricity=sim2_obj.electricity,
            cooling=sim2_obj.cooling,
            heating=sim2_obj.heating,
            hvac=sim2_obj.hvac,
        ),
        energy_saved=energy_saved,
        savings_percent=savings_percent,
    )
