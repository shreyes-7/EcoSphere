"""Typed contracts for REST API request payloads and responses."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from backend.schemas.agent_schemas import AgentRecommendation, OptimizationPlan


class StartOptimizationRequest(BaseModel):
    """Payload to trigger an autonomous closed-loop optimization session."""

    simulation_id: int = Field(ge=1, description="Completed baseline simulation ID")
    max_iterations: int = Field(default=5, ge=1, le=50, description="Maximum optimization iterations")
    target_reduction_percent: float = Field(
        default=15.0, ge=0.0, le=100.0, description="Target energy reduction %"
    )
    min_improvement_threshold_percent: float = Field(
        default=1.0, ge=0.0, le=50.0, description="Minimum improvement % required per iteration"
    )


class ClosedLoopStatusResponse(BaseModel):
    """Status details for a closed-loop run session."""

    closed_loop_run_id: int
    simulation_id: int
    status: str
    max_iterations: int
    current_iteration: int
    total_energy_saved: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SimulationMetricsDetail(BaseModel):
    """Energy metrics summary for a single simulation."""

    id: int
    building_name: str
    total_energy: float | None = None
    electricity: float | None = None
    cooling: float | None = None
    heating: float | None = None
    hvac: float | None = None


class SimulationCompareResponse(BaseModel):
    """Energy comparison details between two simulation runs."""

    simulation_1: SimulationMetricsDetail
    simulation_2: SimulationMetricsDetail
    energy_saved: float
    savings_percent: float


class OptimizationHistoryItem(BaseModel):
    """Summary of a single optimization history record."""

    id: int
    simulation_id: int
    closed_loop_run_id: int | None = None
    iteration: int
    energy_before: float | None = None
    energy_after: float | None = None
    expected_savings: float | None = None
    actual_savings: float | None = None
    final_recommendation: str | None = None
    timestamp: datetime


class OptimizationHistoryListResponse(BaseModel):
    """Paginated list of historical optimization records."""

    total_count: int
    history: list[OptimizationHistoryItem] = Field(default_factory=list)


class DashboardSummaryResponse(BaseModel):
    """Top-level platform analytics and building KPI summary."""

    total_simulations: int
    completed_simulations: int
    total_closed_loop_runs: int
    total_energy_saved_kwh: float
    average_savings_percent: float
    active_agents: int
    latest_recommendation: str | None = None


class LatestAgentRecommendationsResponse(BaseModel):
    """Specialist agent recommendations breakdown."""

    simulation_id: int
    timestamp: datetime
    agents: list[AgentRecommendation] = Field(default_factory=list)
    supervisor_plan: OptimizationPlan | None = None
