from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IncidentRecord(BaseModel):
    incident_id: str = Field(..., description="Unique incident ID")
    timestamp: str = Field(..., description="ISO timestamp")
    category: str = Field(..., description="Category: Energy | Comfort | HVAC | Occupancy | Carbon | Equipment")
    severity: str = Field(..., description="Severity: Low | Medium | High | Critical")
    affected_zones: List[str] = Field(..., description="List of affected thermal zone IDs")
    root_cause: str = Field(..., description="Diagnosed root cause")
    recovery_plan: str = Field(..., description="Generated recovery action plan")
    status: str = Field(..., description="Status: Detected | Recovery Planned | Executed | Resolved")
    resolution_time_sec: Optional[int] = Field(default=None, description="Resolution latency in seconds")

class BuildingHealthScore(BaseModel):
    health_score: int = Field(..., description="Building Health Score [0 - 100]")
    rating: str = Field(..., description="Rating: Excellent | Good | Fair | Poor | Critical")
    active_incidents_count: int = Field(..., description="Count of active incidents")
    resolved_incidents_count: int = Field(..., description="Count of resolved incidents")
    recovery_success_rate_pct: float = Field(..., description="Percentage of successfully executed recoveries")
    energy_waste_prevented_kwh: float = Field(..., description="Accumulated energy waste prevented in kWh")
    active_incidents: List[IncidentRecord] = Field(..., description="List of active building incidents")
