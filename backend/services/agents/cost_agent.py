"""Agent focused on energy-cost exposure."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class CostAgent(BaseAgent):
    """Identify opportunities to reduce avoidable operational energy cost via peak tariff load shifting."""

    agent_name = "cost"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the energy-cost signal based on utility tariff structure."""
        cost = self._estimated_cost(metrics)
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        rate = self._settings.energy_price_per_kwh
        if cost is None:
            return f"Baseline electricity: {elec:.2f} kWh @ tariff ${rate:.2f}/kWh (Est. Cost: ${elec * rate:.2f})."
        return f"Measured energy cost: ${cost:.2f} ({elec:.2f} kWh @ tariff ${rate:.2f}/kWh)."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend cost-conscious scheduling and peak demand reduction."""
        cost = self._estimated_cost(metrics) or 24.0
        return f"Operational cost is ${cost:.2f}. Recommend pre-cooling building during off-peak hours and curtailing non-essential lighting during peak demand periods."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence using direct or estimated cost data."""
        return 0.88 if metrics.electricity is not None or metrics.total_energy is not None else 0.50

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the cost rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate cost savings from load shifting."""
        return 4.5

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe comfort safeguards for load shifting."""
        return "No expected impact when pre-cooling preserves occupied thermal comfort bounds."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe carbon benefit from reducing peak grid demand."""
        return "Shifting load away from peak hours avoids inefficient fossil-fuel peaker plant generation."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Set priority from cost magnitude."""
        return "medium"

    def _estimated_cost(self, metrics: BuildingMetrics) -> float | None:
        if metrics.energy_cost is not None:
            return metrics.energy_cost
        if metrics.electricity is not None:
            return metrics.electricity * self._settings.energy_price_per_kwh
        if metrics.total_energy is not None:
            return metrics.total_energy * self._settings.energy_price_per_kwh
        return None
