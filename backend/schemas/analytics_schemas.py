"""Typed contracts for historical analytics and report exports."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class IterationProgressionPoint(BaseModel):
    """Metrics snapshot at a single iteration step."""

    iteration: int
    total_energy: float
    electricity: float
    cooling: float
    heating: float
    hvac: float
    pmv: float = Field(default=0.0, description="Predicted Mean Vote comfort index")
    carbon_intensity: float = Field(default=0.400, description="Grid carbon intensity kgCO2e/kWh")
    energy_cost: float = Field(default=0.12, description="Energy cost $/kWh")
    recommendation: str | None = None
    timestamp: datetime | None = None


class ClosedLoopAnalyticsResponse(BaseModel):
    """Multi-iteration historical progression analytics report."""

    closed_loop_run_id: int
    simulation_id: int
    status: str
    total_iterations: int
    baseline_energy: float
    final_energy: float
    total_energy_saved_kwh: float
    total_energy_saved_percent: float
    carbon_saved_kg: float
    cost_saved_dollars: float
    comfort_pmv_status: str
    stop_reason: str | None = None
    progression: list[IterationProgressionPoint] = Field(default_factory=list)
