from pydantic import BaseModel, Field
from typing import List, Optional

class ZoneMetric(BaseModel):
    zone_id: str = Field(..., description="Unique thermal zone identifier")
    name: str = Field(..., description="Human-readable zone name (e.g. Conference Room A)")
    floor: str = Field(default="Floor 1", description="Building floor level")
    area_m2: float = Field(default=45.0, description="Zone area in square meters")
    temperature_c: float = Field(..., description="Zone air dry-bulb temperature in °C")
    humidity_pct: float = Field(..., description="Zone relative humidity in %")
    pmv: float = Field(..., description="Predicted Mean Vote thermal comfort index")
    hvac_status: str = Field(..., description="HVAC operational status: Cooling | Heating | Venting | Idle")
    cooling_load_kw: float = Field(default=0.0, description="Active cooling rate in kW")
    heating_load_kw: float = Field(default=0.0, description="Active heating rate in kW")
    occupancy_state: str = Field(default="Occupied", description="Occupancy state: Occupied | Vacant | Reserved")
    comfort_status: str = Field(..., description="Comfort evaluation: Comfortable | Warning | High Demand | Violation")
    agent_recommendation: Optional[str] = Field(default=None, description="Active agent recommendation for this zone")
    color_code: str = Field(..., description="Hex color code or class for map visualization: green | yellow | orange | red | blue | gray")

class BuildingDigitalTwinState(BaseModel):
    building_name: str = Field(..., description="Building identifier")
    simulation_id: Optional[int] = Field(default=None, description="Associated simulation record ID")
    timestamp: str = Field(..., description="ISO timestamp of state calculation")
    total_zones: int = Field(..., description="Total thermal zones")
    average_temperature_c: float = Field(..., description="Mean building temperature in °C")
    average_pmv: float = Field(..., description="Mean PMV thermal comfort across zones")
    total_cooling_kw: float = Field(..., description="Aggregated building cooling load in kW")
    comfort_compliance_pct: float = Field(..., description="Percentage of zones meeting ASHRAE-55 PMV [-0.5, +0.5]")
    zones: List[ZoneMetric] = Field(..., description="List of thermal zone states")

class HeatmapData(BaseModel):
    mode: str = Field(..., description="Heatmap visualization mode: temperature | energy | comfort | carbon")
    unit: str = Field(..., description="Measurement unit (e.g. °C, kW, PMV, kgCO2e/kWh)")
    min_value: float = Field(..., description="Minimum scale value")
    max_value: float = Field(..., description="Maximum scale value")
    zones: List[ZoneMetric] = Field(..., description="Thermal zones with mode-specific values")
