"""SQLAlchemy models for simulations and optimization records."""

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
    optimizations: Mapped[list["Optimization"]] = relationship(back_populates="simulation")


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
