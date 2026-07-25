"""Agent REST APIs for querying specialist agent recommendations and supervisor status."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config import Settings, get_settings
from backend.database.database import get_db
from backend.database.models import Simulation
from backend.schemas.agent_schemas import BuildingMetrics
from backend.schemas.api_schemas import LatestAgentRecommendationsResponse
from backend.services.agents.comfort_agent import ComfortAgent
from backend.services.agents.cost_agent import CostAgent
from backend.services.agents.energy_agent import EnergyAgent
from backend.services.agents.supervisor_agent import create_default_supervisor
from backend.services.agents.sustainability_agent import SustainabilityAgent
from backend.utils.logger import get_logger
from backend.utils.helpers import current_timestamp

router = APIRouter(prefix="/agents", tags=["Agents"])
logger = get_logger(__name__)


@router.get(
    "/latest",
    response_model=LatestAgentRecommendationsResponse,
    summary="Get latest specialist agent recommendations",
)
def get_latest_agent_recommendations(
    simulation_id: int | None = Query(None, description="Optional simulation ID to evaluate"),
    database_session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LatestAgentRecommendationsResponse:
    """Evaluate and return recommendations from Energy, Comfort, Cost, and Sustainability agents."""
    target_sim_id = simulation_id

    if target_sim_id is not None:
        sim = database_session.get(Simulation, target_sim_id)
        if sim is None:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation not found: {target_sim_id}",
            )
    else:
        sim = database_session.query(Simulation).order_by(Simulation.id.desc()).first()
        target_sim_id = sim.id if sim else 1

    metrics = BuildingMetrics(
        simulation_id=target_sim_id,
        total_energy=sim.total_energy if sim and sim.total_energy else 200.0,
        electricity=sim.electricity if sim and sim.electricity else 160.0,
        cooling=sim.cooling if sim and sim.cooling else 70.0,
        heating=sim.heating if sim and sim.heating else 40.0,
        hvac=sim.hvac if sim and sim.hvac else 50.0,
    )

    energy_agent = EnergyAgent(settings)
    comfort_agent = ComfortAgent(settings)
    cost_agent = CostAgent(settings)
    sustainability_agent = SustainabilityAgent(settings)
    supervisor = create_default_supervisor(settings)

    agent_recs = [
        energy_agent.analyze(metrics),
        comfort_agent.analyze(metrics),
        cost_agent.analyze(metrics),
        sustainability_agent.analyze(metrics),
    ]

    supervisor_plan = supervisor.coordinate(metrics)

    logger.info("API GET /agents/latest evaluated for simulation_id=%s", target_sim_id)

    return LatestAgentRecommendationsResponse(
        simulation_id=target_sim_id,
        timestamp=current_timestamp(),
        agents=agent_recs,
        supervisor_plan=supervisor_plan,
    )
