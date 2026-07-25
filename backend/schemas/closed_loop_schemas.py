"""Typed contracts for closed-loop optimization workflows and iteration summaries."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

StopReason = Literal[
    "target_reduction_achieved",
    "min_improvement_threshold_not_met",
    "max_iterations_reached",
    "error",
]


class ClosedLoopConfig(BaseModel):
    """Configurable boundaries and stopping rules for closed-loop optimization."""

    max_iterations: int = Field(
        default=5, ge=1, le=50, description="Maximum optimization iterations to attempt"
    )
    target_reduction_percent: float = Field(
        default=15.0, ge=0.0, le=100.0, description="Target energy reduction percentage"
    )
    min_improvement_threshold_percent: float = Field(
        default=1.0, ge=0.0, le=50.0, description="Minimum improvement % required per iteration"
    )


class ClosedLoopIterationSummary(BaseModel):
    """Performance summary for a single iteration within a closed-loop run."""

    iteration: int = Field(ge=1)
    simulation_id: int
    energy_before: float
    energy_after: float
    expected_savings: float
    actual_savings: float
    cumulative_savings: float
    recommendation: str
    timestamp: datetime | None = None


class ClosedLoopResult(BaseModel):
    """Complete summary of an autonomous closed-loop optimization session."""

    closed_loop_run_id: int
    simulation_id: int
    status: Literal["completed", "failed"]
    total_iterations: int = Field(ge=0)
    baseline_energy: float
    final_energy: float
    total_energy_saved_percent: float
    stop_reason: StopReason
    iterations: list[ClosedLoopIterationSummary] = Field(default_factory=list)
