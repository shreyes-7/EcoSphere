"""Persistence boundary for optimization workflows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.database.models import Optimization, Simulation
from backend.utils.exceptions import OptimizationError


class OptimizationRepository:
    """Read simulation inputs and persist optimization plan records."""

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

    def save_plan(
        self,
        simulation_id: int,
        energy_before: float,
        expected_savings: float,
        recommendation: str,
    ) -> Optimization:
        """Persist a supervisor plan in a transaction."""
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
