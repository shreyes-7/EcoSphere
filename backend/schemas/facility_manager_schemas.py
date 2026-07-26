from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FacilityManagerRequest(BaseModel):
    message: str = Field(..., description="User natural language prompt/question")
    conversation_id: Optional[str] = Field(default="session_default", description="Conversation session ID for multi-turn context")
    building_name: Optional[str] = Field(default="Commercial Test Facility", description="Active building context")

class ToolCallAction(BaseModel):
    tool_name: str = Field(..., description="Executed tool name (e.g. run_simulation, fetch_digital_twin, resolve_incident)")
    status: str = Field(..., description="Execution status: success | error | executed")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments passed to tool")
    result_summary: str = Field(..., description="Brief outcome summary of tool execution")

class FacilityManagerResponse(BaseModel):
    conversation_id: str = Field(..., description="Conversation session ID")
    reply: str = Field(..., description="AI Facility Manager response message")
    role: str = Field(default="facility_manager", description="Response persona role")
    tool_calls: List[ToolCallAction] = Field(default_factory=list, description="Executed backend tool actions")
    context_retrieved: Dict[str, Any] = Field(default_factory=dict, description="Retrieved real building metrics")
    suggested_followups: List[str] = Field(default_factory=list, description="Proactive follow-up question suggestions")
