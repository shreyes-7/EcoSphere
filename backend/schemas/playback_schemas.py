from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PlaybackFrame(BaseModel):
    frame_index: int = Field(..., description="1-indexed sequence frame number")
    timestamp: str = Field(..., description="ISO timestamp")
    event_type: str = Field(..., description="Event type: simulation_start | agent_analysis | supervisor_decision | setpoint_modified | simulation_result")
    title: str = Field(..., description="Frame event summary label")
    electricity_kwh: float = Field(..., description="Electricity consumption")
    hvac_kwh: float = Field(..., description="HVAC energy consumption")
    pmv: float = Field(..., description="PMV comfort metric")
    cooling_setpoint_c: float = Field(..., description="Active cooling setpoint")
    decision_summary: Optional[str] = Field(default=None, description="Supervisor decision summary")
    active_zone_colors: Dict[str, str] = Field(default_factory=dict, description="Synchronized zone ID to color mapping")

class PlaybackSession(BaseModel):
    session_id: str = Field(..., description="Unique playback session identifier")
    simulation_id: Optional[int] = Field(default=None, description="Associated simulation run ID")
    created_at: str = Field(..., description="ISO timestamp")
    total_frames: int = Field(..., description="Total frames in timeline")
    baseline_kwh: float = Field(..., description="Initial baseline energy")
    optimized_kwh: float = Field(..., description="Final optimized energy")
    total_savings_pct: float = Field(..., description="Total energy savings percentage")
    frames: List[PlaybackFrame] = Field(..., description="Chronological timeline frames")
