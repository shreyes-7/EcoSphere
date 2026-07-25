"""Typed contracts for EnergyPlus IDF file modifications."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class IDFModifications(BaseModel):
    """Input parameters for modifying an EnergyPlus building model."""

    cooling_setpoint: float | None = Field(
        default=None, ge=10.0, le=35.0, description="Cooling setpoint in degrees Celsius"
    )
    heating_setpoint: float | None = Field(
        default=None, ge=5.0, le=30.0, description="Heating setpoint in degrees Celsius"
    )
    lighting_multiplier: float | None = Field(
        default=None, ge=0.0, le=2.0, description="Multiplier for lighting power or schedules"
    )
    hvac_schedule_status: str | None = Field(
        default=None, description="HVAC availability status or schedule name"
    )
    occupancy_multiplier: float | None = Field(
        default=None, ge=0.0, le=2.0, description="Multiplier for occupant density or schedules"
    )
    custom_schedule_updates: dict[str, float] | None = Field(
        default=None, description="Custom schedule key-value updates"
    )


class IDFModificationResult(BaseModel):
    """Output contract detailing applied IDF modifications."""

    original_idf_path: str
    modified_idf_path: str
    applied_modifications: dict[str, object]
    timestamp: datetime
