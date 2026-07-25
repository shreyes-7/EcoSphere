"""Independent orchestration service for a single optimization iteration."""

from __future__ import annotations

from backend.schemas.agent_schemas import BuildingMetrics, OptimizationPlan
from backend.schemas.optimization_schemas import AppliedOptimization, OptimizationExecution
from backend.services.agents.supervisor_agent import SupervisorAgent
from backend.services.optimization_repository import OptimizationRepository
from backend.utils.exceptions import OptimizationError
from backend.utils.logger import get_logger


class OptimizationEngine:
    """Create and persist supervisor-approved optimization plans."""

    def __init__(
        self,
        repository: OptimizationRepository,
        supervisor: SupervisorAgent,
    ) -> None:
        """Initialize the engine with persistence and recommendation dependencies."""
        self._repository = repository
        self._supervisor = supervisor
        self._logger = get_logger(__name__)

    def run(self, simulation_id: int, iteration: int = 1) -> OptimizationExecution:
        """Run one independent optimization iteration for a completed simulation.

        Args:
            simulation_id: Completed simulation that supplies baseline metrics.
            iteration: Positive logical iteration number; persistence of detailed
                iteration history is introduced in Phase 3.

        Returns:
            The persisted, supervisor-approved optimization execution.

        Raises:
            OptimizationError: If metrics are unavailable or the plan cannot persist.
        """
        if iteration < 1:
            raise OptimizationError("Optimization iteration must be at least one")

        simulation = self._repository.get_completed_simulation(simulation_id)
        metrics = self.collect_metrics(simulation_id)
        plan = self._supervisor.coordinate(metrics)
        application = self.apply_optimization(plan)
        baseline_energy = (
            simulation.electricity
            if simulation.electricity is not None
            else simulation.total_energy
        )
        if baseline_energy is None:
            raise OptimizationError("Simulation baseline energy is unavailable")

        optimization = self._repository.save_plan(
            simulation_id=simulation_id,
            energy_before=baseline_energy,
            expected_savings=plan.expected_savings,
            recommendation=application.recommendation,
        )
        execution = OptimizationExecution(
            optimization_id=optimization.id,
            simulation_id=simulation_id,
            iteration=iteration,
            metrics=metrics,
            plan=plan,
            application_status=application.status,
        )
        self._logger.info(
            "Optimization plan persisted: simulation_id=%s optimization_id=%s iteration=%s",
            simulation_id,
            optimization.id,
            iteration,
        )
        return execution

    def collect_metrics(self, simulation_id: int) -> BuildingMetrics:
        """Collect available energy metrics from a completed simulation."""
        simulation = self._repository.get_completed_simulation(simulation_id)
        return BuildingMetrics(
            electricity=simulation.electricity,
            cooling=simulation.cooling,
            heating=simulation.heating,
            hvac=simulation.hvac,
        )

    def apply_optimization(self, plan: OptimizationPlan) -> AppliedOptimization:
        """Register an approved plan without modifying the original building model.

        Physical IDF changes intentionally begin in Phase 5. This phase records
        the approved decision so API and MCP layers can reuse the same engine.
        """
        return AppliedOptimization(
            status="planned",
            recommendation=plan.final_recommendation,
        )
