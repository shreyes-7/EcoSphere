"""Persistence boundary for optimization workflows and history tracking."""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from backend.database.models import (
    AgentDecision,
    AgentExplanation,
    ClosedLoopRun,
    MetricsHistory,
    Optimization,
    OptimizationHistory,
    Simulation,
)
from backend.schemas.agent_schemas import BuildingMetrics, OptimizationPlan
from backend.utils.exceptions import OptimizationError


class OptimizationRepository:
    """Read simulation inputs and persist optimization plan and history records."""

    def __init__(self, database_session: Session) -> None:
        """Initialize the repository with a caller-managed database session."""
        self._database_session = database_session

    def get_completed_simulation(self, simulation_id: int) -> Simulation:
        """Return a completed simulation eligible for optimization."""
        simulation = self._database_session.get(Simulation, simulation_id)
        if simulation is None:
            raise OptimizationError(f"Simulation not found: {simulation_id}")
        if simulation.status != "completed":
            raise OptimizationError(
                f"Simulation {simulation_id} must be completed before optimization"
            )
        if simulation.electricity is None and simulation.total_energy is None:
            raise OptimizationError(
                f"Simulation {simulation_id} has no energy metrics to optimize"
            )
        return simulation

    def get_or_create_closed_loop_run(
        self,
        simulation_id: int,
        max_iterations: int = 10,
        target_reduction: float | None = None,
    ) -> ClosedLoopRun:
        """Fetch an existing active closed-loop run or create a new one."""
        self.get_completed_simulation(simulation_id)
        run = (
            self._database_session.query(ClosedLoopRun)
            .filter_by(simulation_id=simulation_id, status="active")
            .first()
        )
        if run is not None:
            return run

        closed_loop_run = ClosedLoopRun(
            simulation_id=simulation_id,
            status="active",
            target_reduction=target_reduction,
            max_iterations=max_iterations,
            current_iteration=1,
        )
        try:
            self._database_session.add(closed_loop_run)
            self._database_session.commit()
            self._database_session.refresh(closed_loop_run)
        except Exception as error:
            self._database_session.rollback()
            raise OptimizationError("Unable to create closed-loop run session") from error

        return closed_loop_run

    def save_plan(
        self,
        simulation_id: int,
        energy_before: float,
        expected_savings: float,
        recommendation: str,
    ) -> Optimization:
        """Persist a supervisor plan in a transaction (legacy Phase 2 wrapper)."""
        optimization = Optimization(
            simulation_id=simulation_id,
            energy_before=energy_before,
            energy_after=None,
            saving_percent=expected_savings,
            recommendation=recommendation,
        )
        try:
            self._database_session.add(optimization)
            self._database_session.commit()
            self._database_session.refresh(optimization)
        except Exception as error:
            self._database_session.rollback()
            raise OptimizationError("Unable to persist optimization plan") from error
        return optimization

    def save_optimization_iteration(
        self,
        simulation_id: int,
        iteration: int,
        energy_before: float,
        metrics: BuildingMetrics,
        plan: OptimizationPlan,
        closed_loop_run_id: int | None = None,
    ) -> tuple[Optimization, OptimizationHistory, MetricsHistory]:
        """Atomically persist Optimization, MetricsHistory, OptimizationHistory, AgentDecisions, and AgentExplanations."""
        try:
            optimization = Optimization(
                simulation_id=simulation_id,
                energy_before=energy_before,
                energy_after=None,
                saving_percent=plan.expected_savings,
                recommendation=plan.final_recommendation,
            )
            self._database_session.add(optimization)

            metrics_history = MetricsHistory(
                simulation_id=simulation_id,
                closed_loop_run_id=closed_loop_run_id,
                iteration=iteration,
                total_energy=metrics.electricity,
                electricity=metrics.electricity,
                cooling=metrics.cooling,
                heating=metrics.heating,
                hvac=metrics.hvac,
                interior_lights=metrics.interior_lights,
                fans=metrics.fans,
                pumps=metrics.pumps,
                indoor_temperature=metrics.indoor_temperature,
                relative_humidity=metrics.relative_humidity,
                pmv=metrics.pmv,
                occupancy=metrics.occupancy,
                outdoor_temperature=metrics.outdoor_temperature,
                carbon_intensity=metrics.carbon_intensity,
                energy_cost=metrics.energy_cost,
            )
            self._database_session.add(metrics_history)

            opt_history = OptimizationHistory(
                simulation_id=simulation_id,
                closed_loop_run_id=closed_loop_run_id,
                iteration=iteration,
                energy_before=energy_before,
                energy_after=None,
                expected_savings=plan.expected_savings,
                actual_savings=None,
                final_recommendation=plan.final_recommendation,
                supervisor_confidence=plan.confidence,
                supervisor_explanation=plan.explanation,
            )
            self._database_session.add(opt_history)
            self._database_session.flush()

            for recommendation in plan.recommendations:
                decision = AgentDecision(
                    optimization_history_id=opt_history.id,
                    agent=recommendation.agent,
                    recommendation=recommendation.recommendation,
                    confidence=recommendation.confidence,
                    expected_savings=recommendation.expected_savings,
                    comfort_impact=recommendation.comfort_impact,
                    carbon_impact=recommendation.carbon_impact,
                    priority=recommendation.priority,
                )
                self._database_session.add(decision)
                self._database_session.flush()

                explanation = AgentExplanation(
                    agent_decision_id=decision.id,
                    reason=recommendation.explanation,
                    detailed_explanation=recommendation.explanation,
                )
                self._database_session.add(explanation)

            if closed_loop_run_id is not None:
                closed_loop_run = self._database_session.get(ClosedLoopRun, closed_loop_run_id)
                if closed_loop_run is not None:
                    closed_loop_run.current_iteration = iteration

            self._database_session.commit()
            self._database_session.refresh(optimization)
            self._database_session.refresh(opt_history)
            self._database_session.refresh(metrics_history)
            return optimization, opt_history, metrics_history
        except Exception as error:
            self._database_session.rollback()
            raise OptimizationError("Unable to persist optimization iteration history") from error

    def get_optimization_history(self, history_id: int) -> OptimizationHistory:
        """Fetch an OptimizationHistory record with joined decisions and explanations."""
        history = (
            self._database_session.query(OptimizationHistory)
            .options(
                joinedload(OptimizationHistory.decisions).joinedload(AgentDecision.explanation)
            )
            .filter_by(id=history_id)
            .first()
        )
        if history is None:
            raise OptimizationError(f"Optimization history not found: {history_id}")
        return history

    def get_optimization_history_by_optimization_id(self, optimization_id: int) -> OptimizationHistory:
        """Fetch an OptimizationHistory record corresponding to an Optimization legacy ID."""
        optimization = self._database_session.get(Optimization, optimization_id)
        if optimization is None:
            raise OptimizationError(f"Optimization record not found: {optimization_id}")

        history = (
            self._database_session.query(OptimizationHistory)
            .options(
                joinedload(OptimizationHistory.decisions).joinedload(AgentDecision.explanation)
            )
            .filter_by(
                simulation_id=optimization.simulation_id,
                final_recommendation=optimization.recommendation,
            )
            .order_by(OptimizationHistory.timestamp.desc())
            .first()
        )
        if history is None:
            raise OptimizationError(f"No history found for optimization: {optimization_id}")
        return history


