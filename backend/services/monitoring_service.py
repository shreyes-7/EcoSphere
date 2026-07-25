"""Service for recording, querying, and aggregating structured logs and telemetry metrics."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from backend.schemas.monitoring_schemas import (
    AgentLatencyBreakdown,
    AgentLogEntry,
    LogSearchResponse,
    SystemMetricsResponse,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MonitoringService:
    """In-memory and repository manager for structured agent execution logs and telemetry."""

    _log_store: ClassVar[list[AgentLogEntry]] = []
    _counter: ClassVar[int] = 0

    @classmethod
    def record_log(
        cls,
        agent: str,
        recommendation: str,
        reason: str,
        confidence: float,
        priority: str,
        execution_time_ms: float,
        expected_savings: float = 0.0,
        level: str = "INFO",
        closed_loop_run_id: int | None = None,
        simulation_id: int | None = None,
    ) -> AgentLogEntry:
        """Record a new structured agent execution log payload."""
        cls._counter += 1
        entry = AgentLogEntry(
            id=cls._counter,
            timestamp=datetime.now(),
            level=level.upper(),
            agent=agent.lower(),
            recommendation=recommendation,
            reason=reason,
            confidence=confidence,
            priority=priority.lower(),
            execution_time_ms=round(execution_time_ms, 2),
            expected_savings=expected_savings,
            closed_loop_run_id=closed_loop_run_id,
            simulation_id=simulation_id,
        )
        cls._log_store.append(entry)

        # Log structured JSON string to python logger
        logger.info(
            "STRUCTURED_AGENT_LOG | agent=%s level=%s latency=%.2fms confidence=%.2f rec='%s'",
            entry.agent,
            entry.level,
            entry.execution_time_ms,
            entry.confidence,
            entry.recommendation,
        )

        return entry

    @classmethod
    def search_logs(
        cls,
        agent: str | None = None,
        level: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> LogSearchResponse:
        """Search and filter stored log entries by agent, level, or text query."""
        filtered = list(cls._log_store)

        if agent:
            filtered = [item for item in filtered if item.agent.lower() == agent.lower()]

        if level:
            filtered = [item for item in filtered if item.level.upper() == level.upper()]

        if query:
            q = query.lower()
            filtered = [
                item
                for item in filtered
                if q in item.recommendation.lower() or q in item.reason.lower() or q in item.agent.lower()
            ]

        # Order by newest first
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        items = filtered[:limit]

        return LogSearchResponse(
            total_count=len(filtered),
            logs=items,
        )

    @classmethod
    def get_system_metrics(cls) -> SystemMetricsResponse:
        """Compute aggregate execution latency and call telemetry."""
        total_evaluations = len(cls._log_store)
        if total_evaluations == 0:
            return SystemMetricsResponse(
                total_evaluations=0,
                avg_execution_time_ms=0.0,
                error_rate_percent=0.0,
                active_agents=4,
                agent_latency=[],
            )

        total_latency = sum(item.execution_time_ms for item in cls._log_store)
        avg_latency = round(total_latency / total_evaluations, 2)

        error_count = sum(1 for item in cls._log_store if item.level == "ERROR")
        error_rate = round((error_count / total_evaluations) * 100.0, 2)

        # Group by agent
        agent_groups: dict[str, list[float]] = {}
        for item in cls._log_store:
            agent_groups.setdefault(item.agent, []).append(item.execution_time_ms)

        breakdown: list[AgentLatencyBreakdown] = []
        for agent_name, latencies in agent_groups.items():
            breakdown.append(
                AgentLatencyBreakdown(
                    agent=agent_name,
                    total_evaluations=len(latencies),
                    avg_latency_ms=round(sum(latencies) / len(latencies), 2),
                    min_latency_ms=round(min(latencies), 2),
                    max_latency_ms=round(max(latencies), 2),
                )
            )

        breakdown.sort(key=lambda x: x.agent)

        return SystemMetricsResponse(
            total_evaluations=total_evaluations,
            avg_execution_time_ms=avg_latency,
            error_rate_percent=error_rate,
            active_agents=4,
            agent_latency=breakdown,
        )
