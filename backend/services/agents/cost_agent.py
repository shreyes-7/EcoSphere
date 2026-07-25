"""Agent focused on energy-cost exposure."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class CostAgent(BaseAgent):
    """Identify opportunities to reduce avoidable operational energy cost."""

    agent_name = "cost"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the available energy-cost signal."""
        cost = self._estimated_cost(metrics)
        if cost is None:
            return "Electricity and energy-cost data are unavailable."
        return f"Estimated energy cost for this run is {cost:.2f}."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend cost-conscious scheduling when data is available."""
        if self._estimated_cost(metrics) is None:
            return "Collect electricity and tariff data before making cost-specific changes."
        return "Shift discretionary HVAC and lighting loads away from costly operating periods."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence using direct or estimated cost data."""
        if metrics.energy_cost is not None:
            return 0.9
        return 0.7 if metrics.electricity is not None else 0.4

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the cost rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate savings only with an available cost signal."""
        return self._settings.max_expected_savings_percent * 0.4 if self._estimated_cost(metrics) is not None else 0.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe comfort safeguards for load shifting."""
        return "No expected impact when discretionary loads exclude occupied comfort periods."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe carbon benefit from reducing avoidable consumption."""
        return "Lower consumption can reduce operational carbon emissions."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Set priority from data completeness."""
        return "medium" if self._estimated_cost(metrics) is not None else "low"

    def _estimated_cost(self, metrics: BuildingMetrics) -> float | None:
        if metrics.energy_cost is not None:
            return metrics.energy_cost
        if metrics.electricity is not None:
            return metrics.electricity * self._settings.energy_price_per_kwh
        return None
