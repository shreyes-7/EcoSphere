"""SQLAlchemy models for simulations and optimization history tracking."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base
from backend.utils.helpers import current_timestamp


class Simulation(Base):
    """A requested EnergyPlus simulation run."""

    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    building_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    weather_file: Mapped[str] = mapped_column(String(1024), nullable=False)
    idf_file: Mapped[str] = mapped_column(String(1024), nullable=False)
    output_folder: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    total_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    electricity: Mapped[float | None] = mapped_column(Float, nullable=True)
    cooling: Mapped[float | None] = mapped_column(Float, nullable=True)
    heating: Mapped[float | None] = mapped_column(Float, nullable=True)
    hvac: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    optimizations: Mapped[list[Optimization]] = relationship(back_populates="simulation")
    closed_loop_runs: Mapped[list[ClosedLoopRun]] = relationship(back_populates="simulation")
    metrics_history: Mapped[list[MetricsHistory]] = relationship(back_populates="simulation")
    optimization_history: Mapped[list[OptimizationHistory]] = relationship(back_populates="simulation")


class Optimization(Base):
    """A future optimization result associated with a simulation."""

    __tablename__ = "optimizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    energy_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    saving_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    simulation: Mapped[Simulation] = relationship(back_populates="optimizations")


class ClosedLoopRun(Base):
    """A multi-iteration closed-loop optimization session."""

    __tablename__ = "closed_loop_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    target_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    current_iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_energy_saved: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    simulation: Mapped[Simulation] = relationship(back_populates="closed_loop_runs")
    metrics_history: Mapped[list[MetricsHistory]] = relationship(back_populates="closed_loop_run")
    optimization_history: Mapped[list[OptimizationHistory]] = relationship(back_populates="closed_loop_run")


class MetricsHistory(Base):
    """Historical snapshot of building energy metrics for an iteration."""

    __tablename__ = "metrics_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    closed_loop_run_id: Mapped[int | None] = mapped_column(ForeignKey("closed_loop_runs.id"), nullable=True)
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    electricity: Mapped[float | None] = mapped_column(Float, nullable=True)
    cooling: Mapped[float | None] = mapped_column(Float, nullable=True)
    heating: Mapped[float | None] = mapped_column(Float, nullable=True)
    hvac: Mapped[float | None] = mapped_column(Float, nullable=True)
    interior_lights: Mapped[float | None] = mapped_column(Float, nullable=True)
    fans: Mapped[float | None] = mapped_column(Float, nullable=True)
    pumps: Mapped[float | None] = mapped_column(Float, nullable=True)
    indoor_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    pmv: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    outdoor_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbon_intensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    simulation: Mapped[Simulation] = relationship(back_populates="metrics_history")
    closed_loop_run: Mapped[ClosedLoopRun | None] = relationship(back_populates="metrics_history")


class OptimizationHistory(Base):
    """Historical record of supervisor optimization decisions per iteration."""

    __tablename__ = "optimization_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    closed_loop_run_id: Mapped[int | None] = mapped_column(ForeignKey("closed_loop_runs.id"), nullable=True)
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    energy_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    supervisor_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    supervisor_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    simulation: Mapped[Simulation] = relationship(back_populates="optimization_history")
    closed_loop_run: Mapped[ClosedLoopRun | None] = relationship(back_populates="optimization_history")
    decisions: Mapped[list[AgentDecision]] = relationship(
        back_populates="optimization_history",
        cascade="all, delete-orphan",
    )


class AgentDecision(Base):
    """Individual agent recommendation snapshot within an optimization iteration."""

    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    optimization_history_id: Mapped[int] = mapped_column(ForeignKey("optimization_history.id"), nullable=False)
    agent: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    expected_savings: Mapped[float] = mapped_column(Float, nullable=False)
    comfort_impact: Mapped[str] = mapped_column(String(255), nullable=False)
    carbon_impact: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    optimization_history: Mapped[OptimizationHistory] = relationship(back_populates="decisions")
    explanation: Mapped[AgentExplanation | None] = relationship(
        back_populates="agent_decision",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AgentExplanation(Base):
    """Detailed reasoning associated with a specific agent decision."""

    __tablename__ = "agent_explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_decision_id: Mapped[int] = mapped_column(
        ForeignKey("agent_decisions.id"), nullable=False, unique=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)

    agent_decision: Mapped[AgentDecision] = relationship(back_populates="explanation")


class RLEpisode(Base):
    """Reinforcement learning training episode record."""

    __tablename__ = "rl_episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state_repr: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    reward: Mapped[float] = mapped_column(Float, nullable=False)
    energy_saved_kwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pmv_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supervisor_accepted: Mapped[bool] = mapped_column(Integer, nullable=False, default=1) # 1=True, 0=False
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)


class RLCheckpoint(Base):
    """Reinforcement learning policy checkpoint persistence."""

    __tablename__ = "rl_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    total_episodes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_reward: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    exploration_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)
    policy_weights_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_timestamp)


