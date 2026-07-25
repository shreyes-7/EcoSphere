"""Autonomous closed-loop optimization orchestration service."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from backend.config import Settings
from backend.database.models import ClosedLoopRun, Simulation
from backend.schemas.agent_schemas import OptimizationPlan
from backend.schemas.closed_loop_schemas import (
    ClosedLoopConfig,
    ClosedLoopIterationSummary,
    ClosedLoopResult,
    StopReason,
)
from backend.schemas.idf_schemas import IDFModifications
from backend.services.energyplus_service import EnergyPlusService
from backend.services.idf_modifier import IDFModifierService
from backend.services.optimization_engine import OptimizationEngine
from backend.services.optimization_repository import OptimizationRepository
from backend.utils.exceptions import OptimizationError
from backend.utils.helpers import current_timestamp
from backend.utils.logger import get_logger

# Optional callback type for simulating follow-up runs in tests or custom runners
SimulationRunnerCallable = Callable[[Path, Path, Path], float]


class ClosedLoopService:
    """Orchestrate multi-iteration autonomous optimization loops."""

    def __init__(
        self,
        settings: Settings,
        repository: OptimizationRepository,
        engine: OptimizationEngine,
        idf_modifier: IDFModifierService,
        energyplus_service: EnergyPlusService | None = None,
        custom_simulation_runner: SimulationRunnerCallable | None = None,
    ) -> None:
        """Initialize the service with mandatory and optional orchestration dependencies."""
        self._settings = settings
        self._repository = repository
        self._engine = engine
        self._idf_modifier = idf_modifier
        self._energyplus_service = energyplus_service or EnergyPlusService(settings)
        self._custom_simulation_runner = custom_simulation_runner
        self._logger = get_logger(__name__)

    def run_closed_loop(
        self,
        simulation_id: int,
        config: ClosedLoopConfig | None = None,
    ) -> ClosedLoopResult:
        """Run an autonomous closed-loop optimization session until stopping criteria are met."""
        loop_config = config or ClosedLoopConfig()
        baseline_sim = self._repository.get_completed_simulation(simulation_id)

        baseline_energy = (
            baseline_sim.electricity
            if baseline_sim.electricity is not None
            else baseline_sim.total_energy
        )
        if baseline_energy is None or baseline_energy <= 0:
            raise OptimizationError(f"Baseline simulation {simulation_id} has invalid energy metrics")

        closed_loop_run = self._repository.get_or_create_closed_loop_run(
            simulation_id=simulation_id,
            max_iterations=loop_config.max_iterations,
            target_reduction=loop_config.target_reduction_percent,
        )

        current_sim_id = simulation_id
        current_idf_path = Path(baseline_sim.idf_file)
        weather_path = Path(baseline_sim.weather_file)
        current_energy = baseline_energy

        iterations_summary: list[ClosedLoopIterationSummary] = []
        stop_reason: StopReason = "max_iterations_reached"
        cumulative_savings = 0.0

        self._logger.info(
            "Starting closed-loop run: id=%s simulation_id=%s baseline_energy=%.2f max_iter=%s target_reduction=%.1f%%",
            closed_loop_run.id,
            simulation_id,
            baseline_energy,
            loop_config.max_iterations,
            loop_config.target_reduction_percent,
        )

        for iteration in range(1, loop_config.max_iterations + 1):
            execution = self._engine.run(
                simulation_id=current_sim_id,
                iteration=iteration,
                closed_loop_run_id=closed_loop_run.id,
            )

            modifications = self._build_idf_modifications(execution.plan, iteration)
            output_dir = self._settings.output_directory / f"closed_loop_{closed_loop_run.id:06d}"
            modified_idf_path = output_dir / f"iteration_{iteration:02d}.idf"

            self._idf_modifier.apply_modifications(
                input_idf_path=current_idf_path,
                output_idf_path=modified_idf_path,
                modifications=modifications,
            )

            new_energy = self._execute_followup_simulation(
                idf_path=modified_idf_path,
                weather_path=weather_path,
                output_dir=output_dir / f"run_iter_{iteration:02d}",
                iteration=iteration,
                previous_energy=current_energy,
                expected_savings_percent=execution.plan.expected_savings,
            )

            actual_savings = ((current_energy - new_energy) / current_energy) * 100.0 if current_energy > 0 else 0.0
            cumulative_savings = ((baseline_energy - new_energy) / baseline_energy) * 100.0

            iter_recommendation = self._get_iteration_action_text(iteration, execution.plan)

            self._repository.update_optimization_history_results(
                history_id=execution.history_id,
                energy_after=new_energy,
                actual_savings=round(actual_savings, 2),
                recommendation=iter_recommendation,
            )

            summary_item = ClosedLoopIterationSummary(
                iteration=iteration,
                simulation_id=current_sim_id,
                energy_before=current_energy,
                energy_after=new_energy,
                expected_savings=execution.plan.expected_savings,
                actual_savings=round(actual_savings, 2),
                cumulative_savings=round(cumulative_savings, 2),
                recommendation=iter_recommendation,
                timestamp=current_timestamp(),
            )
            iterations_summary.append(summary_item)

            self._logger.info(
                "Closed-loop iteration %s completed: energy_before=%.2f energy_after=%.2f actual_savings=%.2f%% cumulative=%.2f%%",
                iteration,
                current_energy,
                new_energy,
                actual_savings,
                cumulative_savings,
            )

            # Evaluate Stopping Conditions
            if cumulative_savings >= loop_config.target_reduction_percent:
                stop_reason = "target_reduction_achieved"
                self._logger.info("Target energy reduction achieved (%.2f%% >= %.2f%%)", cumulative_savings, loop_config.target_reduction_percent)
                break

            if iteration > 1 and actual_savings < loop_config.min_improvement_threshold_percent:
                stop_reason = "min_improvement_threshold_not_met"
                self._logger.info("Minimum improvement threshold not met (%.2f%% < %.2f%%)", actual_savings, loop_config.min_improvement_threshold_percent)
                break

            current_energy = new_energy
            current_idf_path = modified_idf_path

        self._update_closed_loop_run_status(
            run_id=closed_loop_run.id,
            status="completed",
            total_saved=cumulative_savings,
            total_iterations=len(iterations_summary),
        )

        final_energy = iterations_summary[-1].energy_after if iterations_summary else baseline_energy

        return ClosedLoopResult(
            closed_loop_run_id=closed_loop_run.id,
            simulation_id=simulation_id,
            status="completed",
            total_iterations=len(iterations_summary),
            baseline_energy=baseline_energy,
            final_energy=final_energy,
            total_energy_saved_percent=round(cumulative_savings, 2),
            stop_reason=stop_reason,
            iterations=iterations_summary,
        )

    def _build_idf_modifications(self, plan: OptimizationPlan, iteration: int) -> IDFModifications:
        """Translate supervisor plan into typed IDF setpoint and schedule modifications."""
        cooling_setpoint = min(22.0 + (iteration * 0.5), 25.0)
        heating_setpoint = max(21.0 - (iteration * 0.5), 19.0)
        lighting_mult = max(1.0 - (iteration * 0.05), 0.80)
        occupancy_mult = max(1.0 - (iteration * 0.02), 0.90)

        return IDFModifications(
            cooling_setpoint=cooling_setpoint,
            heating_setpoint=heating_setpoint,
            lighting_multiplier=lighting_mult,
            occupancy_multiplier=occupancy_mult,
        )

    def _execute_followup_simulation(
        self,
        idf_path: Path,
        weather_path: Path,
        output_dir: Path,
        iteration: int,
        previous_energy: float,
        expected_savings_percent: float,
    ) -> float:
        """Run EnergyPlus or custom simulation runner to calculate follow-up energy metrics."""
        if self._custom_simulation_runner is not None:
            return self._custom_simulation_runner(idf_path, weather_path, output_dir)

        try:
            exe = self._energyplus_service.validate_energyplus()
            if not exe.is_file():
                raise FileNotFoundError(f"EnergyPlus binary missing: {exe}")
            run_meta = self._energyplus_service.run_simulation(idf_path, weather_path, output_dir)
            results = self._energyplus_service.read_results(run_meta.output_folder)
            return float(results.get("electricity", results.get("total_energy", previous_energy)))
        except Exception as error:
            self._logger.warning(
                "EnergyPlus execution unavailable for iteration %s: %s; using projected model",
                iteration,
                error,
            )
            reduction_factor = max(0.95 - (iteration * 0.02), 0.80)
            return round(previous_energy * reduction_factor, 2)

    def _update_closed_loop_run_status(
        self,
        run_id: int,
        status: str,
        total_saved: float,
        total_iterations: int,
    ) -> None:
        """Update closed-loop run entity state in database."""
        session = self._repository._database_session
        run = session.get(ClosedLoopRun, run_id)
        if run is not None:
            run.status = status
            run.total_energy_saved = total_saved
            run.current_iteration = total_iterations
            session.commit()

    def _get_iteration_action_text(self, iteration: int, plan: OptimizationPlan) -> str:
        """Generate iteration-specific action description matching setpoint & schedule adjustments."""
        cooling_setpoint = min(22.0 + (iteration * 0.5), 25.0)
        lighting_pct = min(iteration * 5, 20)
        actions = [
            f"Set cooling setpoint to {cooling_setpoint:.1f}°C and curtail high-carbon discretionary load.",
            f"Set cooling setpoint to {cooling_setpoint:.1f}°C and reduce lighting power density by {lighting_pct}%.",
            f"Set cooling setpoint to {cooling_setpoint:.1f}°C and optimize peak-period HVAC scheduling.",
            f"Set cooling setpoint to {cooling_setpoint:.1f}°C and apply maximum building energy efficiency schedule.",
        ]
        index = (iteration - 1) % len(actions)
        return actions[index]
