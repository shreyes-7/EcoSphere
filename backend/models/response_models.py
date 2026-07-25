"""Response models for Phase 1 APIs."""

from datetime import datetime

from pydantic import BaseModel


class SimulationResponse(BaseModel):
    """Public representation of a simulation record."""

    id: int
    building_name: str
    status: str
    weather_file: str
    idf_file: str
    output_folder: str | None = None
    total_energy: float | None = None
    electricity: float | None = None
    cooling: float | None = None
    heating: float | None = None
    hvac: float | None = None
    created_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class OptimizationResponse(BaseModel):
    """Public representation of an optimization record."""

    id: int
    simulation_id: int
    energy_before: float | None = None
    energy_after: float | None = None
    saving_percent: float | None = None
    recommendation: str | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Standard API health payload."""

    status: str
    app: str
    version: str


class SimulationResultsResponse(BaseModel):
    """Energy results produced by a completed simulation."""

    status: str
    energy: dict[str, float | None]
