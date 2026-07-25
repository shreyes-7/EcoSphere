"""Agent focused on operational carbon impact."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class SustainabilityAgent(BaseAgent):
    """Recommend actions that lower energy-related carbon emissions."""

    agent_name = "sustainability"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the carbon-intensity signal."""
        carbon_intensity = self._carbon_intensity(metrics)
        if carbon_intensity is None:
            return "Carbon-intensity and electricity data are unavailable."
        return f"Operational carbon intensity is {carbon_intensity:.3f} kgCO2e per kWh."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend carbon-aware load reduction or shifting."""
        carbon_intensity = self._carbon_intensity(metrics)
        if carbon_intensity is None:
            return "Collect electricity and carbon-intensity data before carbon-specific actions."
        if carbon_intensity >= self._settings.high_carbon_intensity_threshold:
            return "Reduce discretionary energy use during high-carbon operating periods."
        return "Maintain efficient operation and prefer lower-carbon operating periods when possible."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence from direct or configured carbon intensity."""
        return 0.9 if metrics.carbon_intensity is not None else 0.65 if metrics.electricity is not None else 0.4

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the sustainability rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate savings when carbon-aware load control is warranted."""
        carbon_intensity = self._carbon_intensity(metrics)
        if carbon_intensity is not None and carbon_intensity >= self._settings.high_carbon_intensity_threshold:
            return self._settings.max_expected_savings_percent * 0.3
        return 0.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe occupant safeguards for carbon-focused operation."""
        return "No expected impact when changes remain within comfort constraints."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the carbon objective."""
        return "Targets lower operational carbon emissions."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Prioritize high-carbon operating conditions."""
        carbon_intensity = self._carbon_intensity(metrics)
        if carbon_intensity is not None and carbon_intensity >= self._settings.high_carbon_intensity_threshold:
            return "high"
        return "medium" if carbon_intensity is not None else "low"

    def _carbon_intensity(self, metrics: BuildingMetrics) -> float | None:
        if metrics.carbon_intensity is not None:
            return metrics.carbon_intensity
        if metrics.electricity is not None:
            return self._settings.carbon_kg_per_kwh
        return None
