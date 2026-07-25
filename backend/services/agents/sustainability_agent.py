"""Agent focused on operational carbon impact."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class SustainabilityAgent(BaseAgent):
    """Recommend actions that lower energy-related carbon emissions based on real grid emissions metrics."""

    agent_name = "sustainability"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the operational carbon emissions signal."""
        carbon_intensity = self._carbon_intensity(metrics) or self._settings.carbon_kg_per_kwh
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        emissions = elec * carbon_intensity
        return f"Operational carbon emissions: {emissions:.2f} kgCO2e ({elec:.2f} kWh @ {carbon_intensity:.3f} kgCO2e/kWh)."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend carbon-aware load reduction or shifting."""
        carbon_intensity = self._carbon_intensity(metrics) or self._settings.carbon_kg_per_kwh
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        emissions = elec * carbon_intensity

        if carbon_intensity >= self._settings.high_carbon_intensity_threshold:
            return f"Grid carbon intensity is high ({carbon_intensity:.3f} kgCO2e/kWh, total emissions {emissions:.1f} kgCO2e). Reduce discretionary energy use during high-carbon operating periods."
        return f"Grid carbon intensity is moderate ({carbon_intensity:.3f} kgCO2e/kWh, total emissions {emissions:.1f} kgCO2e). Maintain energy efficiency."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence from direct or configured carbon intensity."""
        return 0.90 if metrics.electricity is not None or metrics.total_energy is not None else 0.50

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the sustainability rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate savings when carbon-aware load control is warranted."""
        return 3.5

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe occupant safeguards for carbon-focused operation."""
        return "No expected impact when changes remain within comfort constraints."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the carbon objective."""
        return "Targets lower operational carbon emissions."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Prioritize high-carbon operating conditions."""
        carbon_intensity = self._carbon_intensity(metrics) or self._settings.carbon_kg_per_kwh
        if carbon_intensity >= self._settings.high_carbon_intensity_threshold:
            return "high"
        return "medium"

    def _carbon_intensity(self, metrics: BuildingMetrics) -> float | None:
        if metrics.carbon_intensity is not None:
            return metrics.carbon_intensity
        if metrics.electricity is not None or metrics.total_energy is not None:
            return self._settings.carbon_kg_per_kwh
        return None
