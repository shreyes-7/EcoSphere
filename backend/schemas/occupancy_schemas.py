from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ZoneOccupancyProfile(BaseModel):
    zone_id: str = Field(..., description="Unique thermal zone ID")
    name: str = Field(..., description="Thermal zone name")
    state: str = Field(..., description="Occupancy state: Occupied | Partially Occupied | Reserved | Vacant | Maintenance | Closed | Emergency | Unknown")
    priority: str = Field(..., description="Optimization priority: Critical | Normal | Low | Unused | Emergency")
    current_occupants: int = Field(default=0, description="Active occupant count")
    max_capacity: int = Field(default=20, description="Maximum zone capacity")
    scheduled_next_occupancy: Optional[str] = Field(default=None, description="ISO timestamp or text of next scheduled occupancy event")
    pre_conditioning_active: bool = Field(default=False, description="Flag indicating pre-cooling/pre-heating is active")
    hvac_waste_detected: bool = Field(default=False, description="Flag indicating HVAC running without occupants")
    energy_waste_kw: float = Field(default=0.0, description="Estimated wasted HVAC power in kW")

class BuildingOccupancySummary(BaseModel):
    building_name: str = Field(..., description="Building name")
    timestamp: str = Field(..., description="ISO timestamp")
    total_occupied_zones: int = Field(..., description="Count of actively occupied zones")
    total_vacant_zones: int = Field(..., description="Count of vacant/unused zones")
    total_wasted_energy_kw: float = Field(..., description="Aggregated HVAC energy waste across empty zones")
    occupancy_compliance_pct: float = Field(..., description="Percentage of zones with optimal occupancy-aware HVAC control")
    zones: List[ZoneOccupancyProfile] = Field(..., description="Zone occupancy profiles")
    energy_waste_warnings: List[str] = Field(..., description="Active energy waste alert warnings")
