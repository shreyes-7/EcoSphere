"""Internal typed contracts for optimization workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.agent_schemas import BuildingMetrics, OptimizationPlan


class OptimizationExecution(BaseModel):
    """A persisted supervisor plan for one simulation iteration."""

    optimization_id: int
    simulation_id: int
    iteration: int = Field(ge=1)
    metrics: BuildingMetrics
    plan: OptimizationPlan
    application_status: Literal["planned"]


class AppliedOptimization(BaseModel):
    """Result of registering a plan for a later IDF modification phase."""

    status: Literal["planned"]
    recommendation: str
