from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.database import get_db
from backend.schemas.xai_schemas import LiveDecisionFlow
from backend.services.xai_engine import XAIEngineService

router = APIRouter(prefix="/xai", tags=["Explainable AI Decision Engine"])

@router.get("/decision-tree", response_model=LiveDecisionFlow)
def get_live_decision_tree(
    simulation_id: Optional[int] = Query(None, description="Optional simulation ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve live hierarchical Explainable AI (XAI) decision tree and agent reasoning flow.
    """
    return XAIEngineService.build_live_decision_flow(db, simulation_id=simulation_id)
