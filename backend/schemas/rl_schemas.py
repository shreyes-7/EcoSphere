from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RLState(BaseModel):
    outdoor_temp_c: float = Field(..., description="Outdoor dry-bulb temperature")
    indoor_temp_c: float = Field(..., description="Indoor dry-bulb temperature")
    humidity_pct: float = Field(..., description="Relative humidity")
    pmv: float = Field(..., description="PMV comfort index")
    cooling_load_kw: float = Field(..., description="Cooling demand rate")
    electricity_kwh: float = Field(..., description="Total electricity demand")
    carbon_kg_kwh: float = Field(default=0.40, description="Grid carbon intensity")
    occupancy_count: int = Field(default=20, description="Occupant count")

class RLActionRecommendation(BaseModel):
    action: str = Field(..., description="Recommended optimization action")
    expected_reward: float = Field(..., description="Predicted reward metric")
    confidence: float = Field(..., description="Policy confidence [0.0 - 1.0]")
    reasoning: str = Field(..., description="Historical experience rationale")
    safe_limits_satisfied: bool = Field(default=True, description="Safety guardrails check")

class RLEpisodeSummary(BaseModel):
    episode_id: int = Field(..., description="Episode record ID")
    episode_number: int = Field(..., description="Sequence episode number")
    action: str = Field(..., description="Action executed")
    reward: float = Field(..., description="Calculated reward")
    energy_saved_kwh: float = Field(..., description="Energy saved")
    pmv_delta: float = Field(..., description="PMV shift")
    supervisor_accepted: bool = Field(..., description="Supervisor approval status")
    confidence: float = Field(..., description="Policy confidence")
    timestamp: str = Field(..., description="ISO timestamp")

class RLTrainingSummary(BaseModel):
    total_episodes: int = Field(..., description="Total accumulated training episodes")
    average_reward: float = Field(..., description="Average reward across episodes")
    exploration_rate: float = Field(..., description="Current epsilon exploration rate")
    supervisor_acceptance_rate_pct: float = Field(..., description="Percentage of RL advice accepted by Supervisor")
    active_policy_version: str = Field(..., description="Model version")
    recent_episodes: List[RLEpisodeSummary] = Field(..., description="Recent training episodes")
