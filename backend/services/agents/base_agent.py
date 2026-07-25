"""Abstract contract for EcoSphere recommendation agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.config import Settings
from backend.schemas.agent_schemas import AgentRecommendation, BuildingMetrics, Priority
from backend.utils.logger import get_logger


class BaseAgent(ABC):
    """Base class for independently testable building recommendation agents."""

    agent_name: str

    def __init__(self, settings: Settings) -> None:
        """Initialize an agent with its immutable configuration dependency."""
        self._settings = settings
        self._logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    def analyze(self, metrics: BuildingMetrics) -> AgentRecommendation:
        """Build an explainable recommendation from simulation metrics with latency telemetry."""
        import time
        from backend.services.monitoring_service import MonitoringService

        started_at = time.perf_counter()
        recommendation = self.recommend(metrics)
        result = AgentRecommendation(
            agent=self.agent_name,
            recommendation=recommendation,
            confidence=self.confidence_score(metrics),
            explanation=self.explanation(metrics),
            expected_savings=self.expected_savings(metrics),
            comfort_impact=self.comfort_impact(metrics),
            carbon_impact=self.carbon_impact(metrics),
            priority=self.priority(metrics),
        )
        duration_ms = (time.perf_counter() - started_at) * 1000.0

        MonitoringService.record_log(
            agent=self.agent_name,
            recommendation=result.recommendation,
            reason=result.explanation,
            confidence=result.confidence,
            priority=result.priority,
            execution_time_ms=duration_ms,
            expected_savings=result.expected_savings,
        )

        self._logger.info(
            "Agent recommendation produced: agent=%s confidence=%.2f priority=%s latency=%.2fms",
            result.agent,
            result.confidence,
            result.priority,
            duration_ms,
        )
        return result

    @abstractmethod
    def reason(self, metrics: BuildingMetrics) -> str:
        """Return the core evidence behind the agent's recommendation."""

    @abstractmethod
    def recommend(self, metrics: BuildingMetrics) -> str:
        """Return a focused, non-executing building recommendation."""

    @abstractmethod
    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Return a confidence score between zero and one."""

    @abstractmethod
    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return a human-readable explanation for the recommendation."""

    @abstractmethod
    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Return the projected energy-saving percentage."""

    @abstractmethod
    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Return the anticipated occupant-comfort impact."""

    @abstractmethod
    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Return the anticipated carbon impact."""

    @abstractmethod
    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Return the urgency of the recommendation."""
