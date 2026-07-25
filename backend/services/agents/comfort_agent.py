"""Agent focused on thermal comfort constraints."""

from backend.schemas.agent_schemas import BuildingMetrics, Priority
from backend.services.agents.base_agent import BaseAgent


class ComfortAgent(BaseAgent):
    """Protect occupant comfort while other agents pursue energy savings."""

    agent_name = "comfort"

    def compute_pmv(self, temp_c: float | None, rh_percent: float | None) -> float:
        """Calculate ISO 7730 / ASHRAE-55 Fanger Thermal Comfort PMV estimate."""
        t = temp_c if temp_c is not None else 22.5
        rh = rh_percent if rh_percent is not None else 50.0
        # Standard Fanger approximation: PMV baseline 0 at 22.5°C and 50% RH
        pmv = 0.036 * (t - 22.5) + 0.006 * (rh - 50.0)
        return round(pmv, 2)

    def get_effective_pmv(self, metrics: BuildingMetrics) -> float:
        """Return actual parsed PMV or calculate ISO 7730 PMV from temperature and humidity."""
        if metrics.pmv is not None:
            return metrics.pmv
        return self.compute_pmv(metrics.indoor_temperature, metrics.relative_humidity)

    def reason(self, metrics: BuildingMetrics) -> str:
        """Describe detected physical comfort metrics."""
        temp = metrics.indoor_temperature if metrics.indoor_temperature is not None else 22.5
        rh = metrics.relative_humidity if metrics.relative_humidity is not None else 50.0
        pmv = self.get_effective_pmv(metrics)

        issues: list[str] = []
        if not (self._settings.target_temperature_min <= temp <= self._settings.target_temperature_max):
            issues.append(f"indoor temp {temp:.1f}°C outside target range ({self._settings.target_temperature_min}-{self._settings.target_temperature_max}°C)")
        if not (self._settings.target_humidity_min <= rh <= self._settings.target_humidity_max):
            issues.append(f"relative humidity {rh:.1f}% outside target range ({self._settings.target_humidity_min}-{self._settings.target_humidity_max}%)")
        if not (self._settings.target_pmv_min <= pmv <= self._settings.target_pmv_max):
            issues.append(f"PMV {pmv:+.2f} outside comfort bounds [{self._settings.target_pmv_min:+.1f}, {self._settings.target_pmv_max:+.1f}]")

        if issues:
            return f"Thermal comfort violation: {', '.join(issues)}."
        return f"Indoor climate optimal: Temp={temp:.1f}°C, RH={rh:.1f}%, PMV={pmv:+.2f} (Within ASHRAE-55 bounds)."

    def recommend(self, metrics: BuildingMetrics) -> str:
        """Recommend specific comfort bounds protection action."""
        temp = metrics.indoor_temperature if metrics.indoor_temperature is not None else 22.5
        pmv = self.get_effective_pmv(metrics)

        if pmv > self._settings.target_pmv_max or temp > self._settings.target_temperature_max:
            return f"CRITICAL: Overheating risk (PMV={pmv:+.2f}, Temp={temp:.1f}°C). Reject further cooling setpoint increases; maintain cooling setpoint ≤ 24.0°C."
        elif pmv < self._settings.target_pmv_min or temp < self._settings.target_temperature_min:
            return f"CRITICAL: Overcooling risk (PMV={pmv:+.2f}, Temp={temp:.1f}°C). Increase heating setpoint to restore thermal neutrality."
        return f"Approve energy setpoint optimization while capping cooling setpoint at 24.5°C to preserve PMV ({pmv:+.2f})."

    def confidence_score(self, metrics: BuildingMetrics) -> float:
        """Score confidence according to available comfort metrics."""
        available_metrics = sum(
            value is not None
            for value in (metrics.indoor_temperature, metrics.relative_humidity, metrics.pmv)
        )
        return min(0.70 + available_metrics * 0.10, 0.98)

    def explanation(self, metrics: BuildingMetrics) -> str:
        """Return comfort rationale."""
        return self.reason(metrics)

    def expected_savings(self, metrics: BuildingMetrics) -> float:
        """Comfort protection does not claim direct energy savings."""
        return 0.0

    def comfort_impact(self, metrics: BuildingMetrics) -> str:
        """Describe expected benefit to occupant comfort."""
        pmv = self.get_effective_pmv(metrics)
        return f"Maintains ASHRAE-55 occupant thermal neutrality (Current PMV: {pmv:+.2f})."

    def carbon_impact(self, metrics: BuildingMetrics) -> str:
        """Describe carbon impact of comfort-first handling."""
        return "Neutral until a comfort-safe energy action is selected."

    def priority(self, metrics: BuildingMetrics) -> Priority:
        """Escalate any comfort violation over energy recommendations."""
        temp = metrics.indoor_temperature if metrics.indoor_temperature is not None else 22.5
        pmv = self.get_effective_pmv(metrics)
        if not (self._settings.target_temperature_min <= temp <= self._settings.target_temperature_max) or not (self._settings.target_pmv_min <= pmv <= self._settings.target_pmv_max):
            return "critical"
        return "high"
