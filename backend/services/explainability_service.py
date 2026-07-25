"""Service for synthesizing and retrieving explainable AI summaries."""

from __future__ import annotations

from backend.database.models import OptimizationHistory
from backend.schemas.agent_schemas import OptimizationPlan, Priority
from backend.schemas.explainability_schemas import (
    AgentExplanationDetail,
    OptimizationExplanationResponse,
)
from backend.services.optimization_repository import OptimizationRepository
from backend.utils.logger import get_logger


class ExplainabilityService:
    """Service responsible for generating and formatting explainable AI decisions."""

    def __init__(self, repository: OptimizationRepository) -> None:
        """Initialize the explainability service with its repository dependency."""
        self._repository = repository
        self._logger = get_logger(__name__)

    def format_plan_explanation(
        self,
        plan: OptimizationPlan,
        optimization_id: int | None = None,
        history_id: int | None = None,
        simulation_id: int = 1,
        iteration: int = 1,
    ) -> OptimizationExplanationResponse:
        """Synthesize an active OptimizationPlan into a structured explainability response."""
        agent_breakdown: list[AgentExplanationDetail] = [
            AgentExplanationDetail(
                agent=recommendation.agent,
                recommendation=recommendation.recommendation,
                confidence=recommendation.confidence,
                reason=recommendation.explanation,
                expected_savings=recommendation.expected_savings,
                comfort_impact=recommendation.comfort_impact,
                carbon_impact=recommendation.carbon_impact,
                priority=recommendation.priority,
            )
            for recommendation in plan.recommendations
        ]

        comfort_summary = self._synthesize_comfort_impact(agent_breakdown)
        carbon_summary = self._synthesize_carbon_impact(agent_breakdown)

        explanation_response = OptimizationExplanationResponse(
            optimization_id=optimization_id,
            history_id=history_id,
            simulation_id=simulation_id,
            iteration=iteration,
            recommendation=plan.final_recommendation,
            reason=plan.explanation,
            confidence=plan.confidence,
            expected_savings=plan.expected_savings,
            comfort_impact=comfort_summary,
            carbon_impact=carbon_summary,
            agent_breakdown=agent_breakdown,
        )

        self._logger.info(
            "Explainability report generated: simulation_id=%s history_id=%s agents=%s",
            simulation_id,
            history_id,
            len(agent_breakdown),
        )
        return explanation_response

    def get_explanation_by_history_id(self, history_id: int) -> OptimizationExplanationResponse:
        """Retrieve and format an explainable decision report from an OptimizationHistory ID or Simulation ID."""
        try:
            history = self._repository.get_optimization_history(history_id)
            return self._format_history_record(history)
        except Exception:
            histories = self._repository.get_history_by_simulation(history_id)
            if histories:
                return self._format_history_record(histories[-1])
            raise

    def get_explanation_by_optimization_id(self, optimization_id: int) -> OptimizationExplanationResponse:
        """Retrieve and format an explainable decision report from a legacy Optimization ID or Simulation ID."""
        try:
            history = self._repository.get_optimization_history_by_optimization_id(optimization_id)
            return self._format_history_record(history, optimization_id=optimization_id)
        except Exception:
            histories = self._repository.get_history_by_simulation(optimization_id)
            if histories:
                return self._format_history_record(histories[-1])
            raise

    def _format_history_record(
        self,
        history: OptimizationHistory,
        optimization_id: int | None = None,
    ) -> OptimizationExplanationResponse:
        """Transform a database OptimizationHistory record into a typed explainability response."""
        agent_breakdown: list[AgentExplanationDetail] = []
        for decision in history.decisions:
            reason_text = (
                decision.explanation.reason
                if decision.explanation is not None
                else f"Agent {decision.agent} recommended: {decision.recommendation}"
            )
            agent_breakdown.append(
                AgentExplanationDetail(
                    agent=decision.agent,
                    recommendation=decision.recommendation,
                    confidence=decision.confidence,
                    reason=reason_text,
                    expected_savings=decision.expected_savings,
                    comfort_impact=decision.comfort_impact,
                    carbon_impact=decision.carbon_impact,
                    priority=decision.priority,  # type: ignore[arg-type]
                    timestamp=decision.timestamp,
                )
            )

        comfort_summary = self._synthesize_comfort_impact(agent_breakdown)
        carbon_summary = self._synthesize_carbon_impact(agent_breakdown)

        return OptimizationExplanationResponse(
            optimization_id=optimization_id,
            history_id=history.id,
            simulation_id=history.simulation_id,
            iteration=history.iteration,
            recommendation=history.final_recommendation or "No recommendation recorded",
            reason=history.supervisor_explanation or "No explanation recorded",
            confidence=history.supervisor_confidence if history.supervisor_confidence is not None else 0.0,
            expected_savings=history.expected_savings if history.expected_savings is not None else 0.0,
            comfort_impact=comfort_summary,
            carbon_impact=carbon_summary,
            timestamp=history.timestamp,
            agent_breakdown=agent_breakdown,
        )

    def _synthesize_comfort_impact(self, breakdown: list[AgentExplanationDetail]) -> str:
        """Synthesize overall comfort impact across all agent recommendations."""
        comfort_agent = next((item for item in breakdown if item.agent == "comfort"), None)
        if comfort_agent is not None:
            return comfort_agent.comfort_impact
        return "Comfort constraints were evaluated and satisfied."

    def _synthesize_carbon_impact(self, breakdown: list[AgentExplanationDetail]) -> str:
        """Synthesize overall carbon impact across all agent recommendations."""
        sustainability_agent = next((item for item in breakdown if item.agent == "sustainability"), None)
        if sustainability_agent is not None:
            return sustainability_agent.carbon_impact
        return "Reduced energy consumption contributes to lower operational carbon emissions."
