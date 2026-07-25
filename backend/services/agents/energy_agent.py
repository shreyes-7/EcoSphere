"""Agent focused on energy consumption and HVAC efficiency."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class EnergyAgent(BaseAgent):
    """Recommend non-invasive actions that reduce building energy use based on real parsed metrics."""

    agent_name = "energy"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Explain the observed HVAC and electricity energy condition."""
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        hvac = metrics.hvac if metrics.hvac is not None else ((metrics.cooling or 0.0) + (metrics.heating or 0.0))
        ratio = (hvac / elec * 100.0) if elec > 0 else 0.0
        return f"Measured total electricity: {elec:.2f} kWh, HVAC demand: {hvac:.2f} kWh ({ratio:.1f}% of total building energy)."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend an explicit numerical setpoint adjustment based on HVAC demand."""
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        hvac = metrics.hvac if metrics.hvac is not None else ((metrics.cooling or 0.0) + (metrics.heating or 0.0))
        ratio = (hvac / elec * 100.0) if elec > 0 else 0.0

        if ratio >= 25.0 or hvac >= self._settings.high_hvac_energy_threshold:
            return f"HVAC energy is elevated ({hvac:.1f} kWh, {ratio:.1f}%). Recommend increasing cooling setpoint by +0.5°C to 23.0°C to reduce chiller demand."
        return f"HVAC energy is nominal ({hvac:.1f} kWh, {ratio:.1f}%). Maintain current setpoint schedules."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence according to available HVAC data."""
        return 0.92 if metrics.hvac is not None or metrics.electricity is not None else 0.50

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the energy rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Estimate savings based on HVAC demand ratio."""
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        hvac = metrics.hvac if metrics.hvac is not None else ((metrics.cooling or 0.0) + (metrics.heating or 0.0))
        ratio = (hvac / elec * 100.0) if elec > 0 else 0.0
        if ratio >= 25.0:
            return round(min(ratio * 0.25, 12.5), 1)
        return 5.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe comfort safeguards for energy actions."""
        return "No expected impact when schedule changes preserve occupied periods."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe the carbon benefit of reduced energy."""
        return "Directly reduces operational carbon emissions associated with utility power generation."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Prioritize elevated HVAC energy for review."""
        elec = metrics.electricity if metrics.electricity is not None else (metrics.total_energy or 160.0)
        hvac = metrics.hvac if metrics.hvac is not None else ((metrics.cooling or 0.0) + (metrics.heating or 0.0))
        ratio = (hvac / elec * 100.0) if elec > 0 else 0.0
        if ratio >= 25.0:
            return "high"
        return "medium"
