"""Agent focused on energy consumption and HVAC efficiency."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class EnergyAgent(BaseAgent):
    """Recommend non-invasive actions that reduce building energy use."""

    agent_name = "energy"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the observed HVAC energy condition."""
        if metrics.hvac is None:
            return "HVAC energy data is unavailable; the recommendation is precautionary."
        return f"Measured HVAC energy is {metrics.hvac:.2f} kWh."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend an energy action based on HVAC demand."""
        if metrics.hvac is not None and metrics.hvac >= self._settings.high_hvac_energy_threshold:
            return "Review HVAC schedules and reduce conditioning during unoccupied periods."
        return "Maintain current HVAC scheduling and continue monitoring energy demand."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence according to available HVAC data."""
        return 0.9 if metrics.hvac is not None else 0.45

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the energy rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate savings only when HVAC demand is elevated."""
        if metrics.hvac is not None and metrics.hvac >= self._settings.high_hvac_energy_threshold:
            return self._settings.max_expected_savings_percent
        return 0.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe comfort safeguards for energy actions."""
        return "No expected impact when schedule changes preserve occupied periods."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the carbon benefit of reduced energy."""
        return "Reduced HVAC energy lowers associated operational carbon emissions."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Prioritize elevated HVAC energy for review."""
        if metrics.hvac is not None and metrics.hvac >= self._settings.high_hvac_energy_threshold:
            return "high"
        return "low"
