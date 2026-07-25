"""Typed contracts for explainable AI summaries and decision rationale."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from backend.schemas.agent_schemas import Priority


class AgentExplanationDetail(BaseModel):
    """Detailed explainable breakdown for a single specialist agent's recommendation."""

    agent: str
    recommendation: str
    confidence: float = Field(ge=0, le=1)
    reason: str
    expected_savings: float = Field(ge=0, le=100)
    comfort_impact: str
    carbon_impact: str
    priority: Priority
    timestamp: datetime | None = None


class OptimizationExplanationResponse(BaseModel):
    """Structured explainable AI report for an optimization decision."""

    optimization_id: int | None = None
    history_id: int | None = None
    simulation_id: int
    iteration: int = Field(ge=1)
    recommendation: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    expected_savings: float = Field(ge=0, le=100)
    comfort_impact: str
    carbon_impact: str
    timestamp: datetime | None = None
    agent_breakdown: list[AgentExplanationDetail] = Field(default_factory=list)
