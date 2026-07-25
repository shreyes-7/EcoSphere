"""Internal typed contracts for optimization workflows and historical tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.agent_schemas import BuildingMetrics, OptimizationPlan, Priority


class AppliedOptimization(BaseModel):
    """Result of registering a plan for a later IDF modification phase."""

    status: Literal["planned"]
    recommendation: str


class AgentExplanationRecord(BaseModel):
    """Persisted explanation details for an agent decision."""

    id: int
    agent_decision_id: int
    reason: str
    detailed_explanation: str | None = None
    timestamp: datetime


class AgentDecisionRecord(BaseModel):
    """Persisted agent decision snapshot."""

    id: int
    optimization_history_id: int
    agent: str
    recommendation: str
    confidence: float = Field(ge=0, le=1)
    expected_savings: float = Field(ge=0, le=100)
    comfort_impact: str
    carbon_impact: str
    priority: Priority
    timestamp: datetime
    explanation: AgentExplanationRecord | None = None


class OptimizationHistoryRecord(BaseModel):
    """Persisted supervisor optimization history for one iteration."""

    id: int
    simulation_id: int
    closed_loop_run_id: int | None = None
    iteration: int = Field(ge=1)
    energy_before: float | None = None
    energy_after: float | None = None
    expected_savings: float | None = None
    actual_savings: float | None = None
    final_recommendation: str | None = None
    supervisor_confidence: float | None = None
    supervisor_explanation: str | None = None
    timestamp: datetime
    decisions: list[AgentDecisionRecord] = Field(default_factory=list)


class MetricsHistoryRecord(BaseModel):
    """Persisted snapshot of building metrics for an iteration."""

    id: int
    simulation_id: int
    closed_loop_run_id: int | None = None
    iteration: int = Field(ge=1)
    metrics: BuildingMetrics
    timestamp: datetime


class ClosedLoopRunRecord(BaseModel):
    """Persisted closed-loop optimization session metadata."""

    id: int
    simulation_id: int
    status: str
    target_reduction: float | None = None
    max_iterations: int = Field(ge=1, default=10)
    current_iteration: int = Field(ge=1, default=1)
    total_energy_saved: float | None = None
    created_at: datetime
    updated_at: datetime


class OptimizationExecution(BaseModel):
    """A persisted supervisor plan and history for one simulation iteration."""

    optimization_id: int
    history_id: int | None = None
    closed_loop_run_id: int | None = None
    simulation_id: int
    iteration: int = Field(ge=1)
    metrics: BuildingMetrics
    plan: OptimizationPlan
    application_status: Literal["planned"]

