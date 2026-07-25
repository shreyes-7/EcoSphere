"""Typed contracts for structured logging, telemetry, and system monitoring."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class AgentLogEntry(BaseModel):
    """Structured log payload emitted during agent execution."""

    id: int | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    level: str = Field(default="INFO", description="Log level: INFO, WARNING, ERROR")
    agent: str = Field(..., description="Agent name: energy, comfort, cost, sustainability, supervisor")
    recommendation: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    priority: str = Field(default="medium")
    execution_time_ms: float = Field(ge=0, description="Agent execution latency in milliseconds")
    expected_savings: float = Field(default=0.0)
    closed_loop_run_id: int | None = None
    simulation_id: int | None = None


class LogSearchRequest(BaseModel):
    """Filter criteria for searching system logs."""

    agent: str | None = None
    level: str | None = None
    query: str | None = None
    limit: int = Field(default=50, ge=1, le=500)


class LogSearchResponse(BaseModel):
    """Search results response for structured logs."""

    total_count: int
    logs: list[AgentLogEntry]


class AgentLatencyBreakdown(BaseModel):
    """Average execution latency per agent."""

    agent: str
    total_evaluations: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float


class SystemMetricsResponse(BaseModel):
    """Top-level system telemetry metrics."""

    total_evaluations: int
    avg_execution_time_ms: float
    error_rate_percent: float
    active_agents: int = 4
    agent_latency: list[AgentLatencyBreakdown]
