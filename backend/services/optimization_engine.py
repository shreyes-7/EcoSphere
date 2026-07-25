"""Independent orchestration service for a single optimization iteration."""

from __future__ import annotations

from backend.schemas.agent_schemas import BuildingMetrics, OptimizationPlan
from backend.schemas.optimization_schemas import AppliedOptimization, OptimizationExecution
from backend.services.agents.supervisor_agent import SupervisorAgent
from backend.services.optimization_repository import OptimizationRepository
from backend.utils.exceptions import OptimizationError
from backend.utils.logger import get_logger


class OptimizationEngine:
    """Create and persist supervisor-approved optimization plans and history records."""

    def __init__(
        self,
        repository: OptimizationRepository,
        supervisor: SupervisorAgent,
    ) -> None:
        """Initialize the engine with persistence and recommendation dependencies."""
        self._repository = repository
        self._supervisor = supervisor
        self._logger = get_logger(__name__)

    def run(
        self,
        simulation_id: int,
        iteration: int = 1,
        closed_loop_run_id: int | None = None,
    ) -> OptimizationExecution:
        """Run one independent optimization iteration for a completed simulation.

        Args:
            simulation_id: Completed simulation that supplies baseline metrics.
            iteration: Positive logical iteration number.
            closed_loop_run_id: Optional ID of an existing closed-loop run session.

        Returns:
            The persisted, supervisor-approved optimization execution including history IDs.

        Raises:
            OptimizationError: If metrics are unavailable or history cannot persist.
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

        closed_loop_run = (
            self._repository.get_or_create_closed_loop_run(simulation_id)
            if closed_loop_run_id is None
            else None
        )
        effective_run_id = (
            closed_loop_run_id
            if closed_loop_run_id is not None
            else (closed_loop_run.id if closed_loop_run else None)
        )

        optimization, opt_history, metrics_hist = self._repository.save_optimization_iteration(
            simulation_id=simulation_id,
            iteration=iteration,
            energy_before=baseline_energy,
            metrics=metrics,
            plan=plan,
            closed_loop_run_id=effective_run_id,
        )

        execution = OptimizationExecution(
            optimization_id=optimization.id,
            history_id=opt_history.id,
            closed_loop_run_id=effective_run_id,
            simulation_id=simulation_id,
            iteration=iteration,
            metrics=metrics,
            plan=plan,
            application_status=application.status,
        )
        self._logger.info(
            "Optimization history persisted: simulation_id=%s optimization_id=%s history_id=%s iteration=%s",
            simulation_id,
            optimization.id,
            opt_history.id,
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

