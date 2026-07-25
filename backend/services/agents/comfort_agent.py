"""Agent focused on thermal comfort constraints."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class ComfortAgent(BaseAgent):
    """Protect occupant comfort while other agents pursue energy savings."""

    agent_name = "comfort"

    def reason(self, metrics: BuildingMetrics) -> str:
        """Describe the detected comfort condition."""
        issues: list[str] = []
        if metrics.indoor_temperature is not None and not self._temperature_is_comfortable(metrics):
            issues.append(f"indoor temperature is {metrics.indoor_temperature:.1f}°C")
        if metrics.relative_humidity is not None and not self._humidity_is_comfortable(metrics):
            issues.append(f"relative humidity is {metrics.relative_humidity:.1f}%")
        if metrics.pmv is not None and not self._pmv_is_comfortable(metrics):
            issues.append(f"PMV is {metrics.pmv:.2f}")
        return "Comfort constraint detected: " + ", ".join(issues) if issues else "Available comfort metrics are within configured targets."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend preserving or restoring configured comfort bounds."""
        if self._has_comfort_issue(metrics):
            return "Prioritize restoring configured temperature, humidity, and PMV comfort targets before energy reductions."
        return "Preserve current comfort conditions while considering energy-saving actions."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence according to the number of available comfort metrics."""
        available_metrics = sum(
            value is not None
            for value in (metrics.indoor_temperature, metrics.relative_humidity, metrics.pmv)
        )
        return min(0.5 + available_metrics * 0.15, 0.95)

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return the comfort rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Comfort protection does not claim direct energy savings."""
        return 0.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe expected benefit to occupant comfort."""
        return "Protects configured thermal-comfort constraints."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe carbon impact of comfort-first handling."""
        return "Neutral until a comfort-safe energy action is selected."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Escalate any comfort violation over energy recommendations."""
        return "critical" if self._has_comfort_issue(metrics) else "medium"

    def _has_comfort_issue(self, metrics: BuildingMetrics) -> bool:
        return not (
            self._temperature_is_comfortable(metrics)
            and self._humidity_is_comfortable(metrics)
            and self._pmv_is_comfortable(metrics)
        )

    def _temperature_is_comfortable(self, metrics: BuildingMetrics) -> bool:
        return metrics.indoor_temperature is None or (
            self._settings.target_temperature_min
            <= metrics.indoor_temperature
            <= self._settings.target_temperature_max
        )

    def _humidity_is_comfortable(self, metrics: BuildingMetrics) -> bool:
        return metrics.relative_humidity is None or (
            self._settings.target_humidity_min
            <= metrics.relative_humidity
            <= self._settings.target_humidity_max
        )

    def _pmv_is_comfortable(self, metrics: BuildingMetrics) -> bool:
        return metrics.pmv is None or (
            self._settings.target_pmv_min <= metrics.pmv <= self._settings.target_pmv_max
        )
