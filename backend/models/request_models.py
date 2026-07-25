"""Request models for Phase 1 APIs."""

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Input required to register a simulation request."""

    building_name: str = Field(min_length=1, max_length=255)
    weather_file: str = Field(min_length=1)
    idf_file: str = Field(min_length=1)


class OptimizationRequest(BaseModel):
    """Input for a future optimization request."""

    simulation_id: int = Field(gt=0)
    goal: str = Field(min_length=1, max_length=500)


class ChatRequest(BaseModel):
    """Prompt forwarded to the configured Ollama model."""

    prompt: str = Field(min_length=1, max_length=20_000)
