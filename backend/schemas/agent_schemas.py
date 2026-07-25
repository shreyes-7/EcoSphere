"""Typed contracts for the multi-agent framework."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high", "critical"]


class BuildingMetrics(BaseModel):
    """Simulation metrics used by recommendation agents."""

    electricity: float | None = Field(default=None, ge=0)
    cooling: float | None = Field(default=None, ge=0)
    heating: float | None = Field(default=None, ge=0)
    hvac: float | None = Field(default=None, ge=0)
    interior_lights: float | None = Field(default=None, ge=0)
    fans: float | None = Field(default=None, ge=0)
    pumps: float | None = Field(default=None, ge=0)
    indoor_temperature: float | None = None
    relative_humidity: float | None = Field(default=None, ge=0, le=100)
    pmv: float | None = None
    occupancy: float | None = Field(default=None, ge=0)
    outdoor_temperature: float | None = None
    carbon_intensity: float | None = Field(default=None, ge=0)
    energy_cost: float | None = Field(default=None, ge=0)


class AgentRecommendation(BaseModel):
    """An explainable recommendation produced by one specialized agent."""

    agent: str
    recommendation: str
    confidence: float = Field(ge=0, le=1)
    explanation: str
    expected_savings: float = Field(ge=0, le=100)
    comfort_impact: str
    carbon_impact: str
    priority: Priority


class OptimizationPlan(BaseModel):
    """The supervisor's resolved plan across all agent recommendations."""

    recommendations: list[AgentRecommendation]
    final_recommendation: str
    confidence: float = Field(ge=0, le=1)
    explanation: str
    expected_savings: float = Field(ge=0, le=100)
