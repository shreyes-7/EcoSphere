"""Supervisor that coordinates specialized building recommendation agents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.config import Settings
from backend.schemas.agent_schemas import AgentRecommendation, BuildingMetrics, OptimizationPlan, Priority
from backend.services.agents.base_agent import BaseAgent
from backend.services.agents.comfort_agent import ComfortAgent
from backend.services.agents.cost_agent import CostAgent
from backend.services.agents.energy_agent import EnergyAgent
from backend.services.agents.sustainability_agent import SustainabilityAgent

_PRIORITY_ORDER: dict[Priority, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


class SupervisorAgent(BaseAgent):
    """Coordinate specialized agents and resolve their competing priorities."""

    agent_name = "supervisor"

    def __init__(self, settings: Settings, agents: Sequence[BaseAgent]) -> None:
        """Initialize the supervisor with its configured specialist agents."""
        super().__init__(settings)
        if not agents:
            raise ValueError("SupervisorAgent requires at least one specialist agent")
        self._agents = tuple(agents)

    def coordinate(self, metrics: BuildingMetrics) -> OptimizationPlan:
        """Collect specialist recommendations and produce a resolved final plan."""
        import time
        from backend.services.monitoring_service import MonitoringService

        started_at = time.perf_counter()
        recommendations = [agent.analyze(metrics) for agent in self._agents]
        resolved_recommendations = self.resolve_conflicts(recommendations)
        plan = OptimizationPlan(
            recommendations=resolved_recommendations,
            final_recommendation=self._final_recommendation(resolved_recommendations),
            confidence=self._plan_confidence(resolved_recommendations),
            explanation=self._plan_explanation(resolved_recommendations),
            expected_savings=self._plan_savings(resolved_recommendations),
        )
        duration_ms = (time.perf_counter() - started_at) * 1000.0

        MonitoringService.record_log(
            agent=self.agent_name,
            recommendation=plan.final_recommendation,
            reason=plan.explanation,
            confidence=plan.confidence,
            priority="high",
            execution_time_ms=duration_ms,
            expected_savings=plan.expected_savings,
        )

        self._logger.info(
            "Supervisor plan produced: recommendations=%s confidence=%.2f latency=%.2fms",
            len(plan.recommendations),
            plan.confidence,
            duration_ms,
        )
        return plan

    def resolve_conflicts(
        self, recommendations: Sequence[AgentRecommendation]
    ) -> list[AgentRecommendation]:
        """Order recommendations so critical comfort constraints cannot be overridden."""
        return sorted(
            recommendations,
            key=lambda recommendation: (
                _PRIORITY_ORDER[recommendation.priority],
                recommendation.confidence,
            ),
            reverse=True,
        )

    def analyze(self, metrics: BuildingMetrics) -> AgentRecommendation:
        """Represent the coordinated plan through the BaseAgent contract."""
        plan = self.coordinate(metrics)
        return AgentRecommendation(
            agent=self.agent_name,
            recommendation=plan.final_recommendation,
            confidence=plan.confidence,
            explanation=plan.explanation,
            expected_savings=plan.expected_savings,
            comfort_impact="Comfort recommendations are prioritized over energy savings.",
            carbon_impact="The plan includes sustainability recommendations when data is available.",
            priority="critical" if self._has_critical_comfort_constraint(plan) else "high",
        )

    def reason(self, metrics: BuildingMetrics) -> str:
        """Return the reason from the current coordinated plan."""
        return self.coordinate(metrics).explanation

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Return the final action from the current coordinated plan."""
        return self.coordinate(metrics).final_recommendation

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Return the confidence from the current coordinated plan."""
        return self.coordinate(metrics).confidence

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the explanation from the current coordinated plan."""
        return self.coordinate(metrics).explanation

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Return the expected savings from the current coordinated plan."""
        return self.coordinate(metrics).expected_savings

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the supervisor's comfort rule."""
        return "Comfort constraints take precedence over all energy and cost recommendations."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the supervisor's carbon rule."""
        return "Carbon recommendations are considered after comfort constraints are satisfied."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Return priority according to the coordinated plan."""
        return "critical" if self._has_critical_comfort_constraint(self.coordinate(metrics)) else "high"

    def _has_critical_comfort_constraint(self, plan: OptimizationPlan) -> bool:
        return any(
            recommendation.agent == "comfort" and recommendation.priority == "critical"
            for recommendation in plan.recommendations
        )

    def _final_recommendation(self, recommendations: Sequence[AgentRecommendation]) -> str:
        comfort_recommendation = next(
            (
                recommendation
                for recommendation in recommendations
                if recommendation.agent == "comfort" and recommendation.priority == "critical"
            ),
            None,
        )
        if comfort_recommendation is not None:
            return comfort_recommendation.recommendation
        return recommendations[0].recommendation

    def _plan_confidence(self, recommendations: Sequence[AgentRecommendation]) -> float:
        return round(sum(item.confidence for item in recommendations) / len(recommendations), 2)

    def _plan_explanation(self, recommendations: Sequence[AgentRecommendation]) -> str:
        leading_agents = ", ".join(item.agent for item in recommendations[:2])
        return f"The plan prioritizes recommendations from: {leading_agents}."

    def _plan_savings(self, recommendations: Sequence[AgentRecommendation]) -> float:
        estimated_savings = sum(item.expected_savings for item in recommendations)
        return min(round(estimated_savings, 2), self._settings.max_expected_savings_percent)

    def execute_mcp_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke an EcoSphere MCP building intelligence tool on behalf of the supervisor agent."""
        from backend.mcp import tools as mcp_tools

        tool_map = {
            "run_simulation": mcp_tools.run_simulation_tool,
            "modify_idf": mcp_tools.modify_idf_tool,
            "read_results": mcp_tools.read_results_tool,
            "compare_runs": mcp_tools.compare_runs_tool,
            "history": mcp_tools.history_tool,
            "optimize_building": mcp_tools.optimize_building_tool,
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown MCP tool: '{tool_name}'. Available tools: {list(tool_map.keys())}")

        self._logger.info("Supervisor invoking MCP tool '%s' with arguments: %s", tool_name, list(arguments.keys()))
        handler = tool_map[tool_name]
        return handler(**arguments)



def create_default_supervisor(settings: Settings) -> SupervisorAgent:
    """Build the standard EcoSphere supervisor with all specialist agents."""
    return SupervisorAgent(
        settings,
        agents=(
            EnergyAgent(settings),
            ComfortAgent(settings),
            CostAgent(settings),
            SustainabilityAgent(settings),
        ),
    )
