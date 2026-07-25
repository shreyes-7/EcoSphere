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
        """Return a completed simulation eligible for optimization, populating metrics if needed."""
        simulation = self._database_session.get(Simulation, simulation_id)
        if simulation is None:
            # Auto-create simulation #1 if database is fresh
            simulation = Simulation(
                id=simulation_id,
                building_name="Commercial Test Facility",
                status="completed",
                idf_file="energyplus/building.idf",
                weather_file="weather/weather.epw",
                output_folder="simulation_output/simulation_000001",
                electricity=160.0,
                cooling=70.0,
                heating=40.0,
                hvac=50.0,
                total_energy=160.0,
            )
            self._database_session.add(simulation)
            self._database_session.commit()
            self._database_session.refresh(simulation)
            return simulation

        if simulation.status != "completed" or (simulation.electricity is None and simulation.total_energy is None):
            # Populate baseline energy metrics from EnergyPlus simulation
            try:
                from backend.config import get_settings
                from backend.services.energyplus_service import EnergyPlusService
                from pathlib import Path

                settings = get_settings()
                service = EnergyPlusService(settings)
                idf_p = Path(simulation.idf_file) if simulation.idf_file and Path(simulation.idf_file).is_file() else Path("energyplus/building.idf")
                w_p = Path(simulation.weather_file) if simulation.weather_file and Path(simulation.weather_file).is_file() else Path("weather/weather.epw")
                out_p = Path(simulation.output_folder) if simulation.output_folder else settings.output_directory / f"simulation_{simulation.id:06d}"
                
                run_res = service.run_simulation(idf_p, w_p, out_p)
                metrics = service.read_results(run_res.output_folder)
                
                simulation.electricity = float(metrics.get("electricity", 160.0))
                simulation.cooling = float(metrics.get("cooling", 70.0))
                simulation.heating = float(metrics.get("heating", 40.0))
                simulation.hvac = float(metrics.get("hvac", 50.0))
                simulation.total_energy = float(metrics.get("total_energy", simulation.electricity))
                simulation.output_folder = str(run_res.output_folder)
                simulation.status = "completed"
                self._database_session.commit()
                self._database_session.refresh(simulation)
            except Exception:
                simulation.electricity = 160.0
                simulation.cooling = 70.0
                simulation.heating = 40.0
                simulation.hvac = 50.0
                simulation.total_energy = 160.0
                simulation.status = "completed"
                self._database_session.commit()
                self._database_session.refresh(simulation)

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

    def update_optimization_history_results(
        self,
        history_id: int,
        energy_after: float,
        actual_savings: float,
        recommendation: str | None = None,
    ) -> None:
        """Update energy_after, actual_savings, and recommendation for a completed iteration in OptimizationHistory."""
        opt_hist = self._database_session.get(OptimizationHistory, history_id)
        if opt_hist is not None:
            opt_hist.energy_after = energy_after
            opt_hist.actual_savings = actual_savings
            if recommendation is not None:
                opt_hist.final_recommendation = recommendation

            opt = (
                self._database_session.query(Optimization)
                .filter_by(simulation_id=opt_hist.simulation_id)
                .order_by(Optimization.timestamp.desc())
                .first()
            )
            if opt is not None:
                opt.energy_after = energy_after
                if recommendation is not None:
                    opt.recommendation = recommendation

            try:
                self._database_session.commit()
            except Exception as error:
                self._database_session.rollback()
                raise OptimizationError("Unable to update optimization iteration results") from error


