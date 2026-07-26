from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DecisionTreeNode(BaseModel):
    id: str = Field(..., description="Node unique ID")
    title: str = Field(..., description="Node title (e.g. Energy Agent Evaluation)")
    category: str = Field(..., description="Category: agent | rl | supervisor | simulation | action")
    status: str = Field(..., description="Status: approved | rejected | conflict | info")
    agent_name: Optional[str] = Field(default=None, description="Associated agent name")
    recommendation: Optional[str] = Field(default=None, description="Recommended proposal")
    reasoning: str = Field(..., description="Human-readable decision explanation")
    confidence: float = Field(default=0.90, description="Confidence score")
    expected_savings: float = Field(default=0.0, description="Expected kWh savings")
    children: List['DecisionTreeNode'] = Field(default_factory=list, description="Child decision nodes")

class ConflictItem(BaseModel):
    conflict_id: str = Field(..., description="Conflict ID")
    proposing_agent: str = Field(..., description="Proposing agent name")
    proposal: str = Field(..., description="Agent proposal")
    opposing_agent: str = Field(..., description="Opposing agent name")
    objection_reason: str = Field(..., description="Reason for objection")
    supervisor_resolution: str = Field(..., description="Final resolution by Supervisor")

class LiveDecisionFlow(BaseModel):
    simulation_id: Optional[int] = Field(default=None, description="Simulation ID")
    iteration: int = Field(default=1, description="Closed loop iteration")
    timestamp: str = Field(..., description="ISO timestamp")
    root_node: DecisionTreeNode = Field(..., description="Hierarchical decision tree root")
    conflicts: List[ConflictItem] = Field(..., description="Detected conflicts and supervisor resolutions")
