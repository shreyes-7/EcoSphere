from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.rl_schemas import RLState, RLActionRecommendation, RLTrainingSummary, RLEpisodeSummary
from backend.services.rl_engine import RLEngineService

router = APIRouter(prefix="/rl", tags=["Reinforcement Learning Engine"])

@router.get("/summary", response_model=RLTrainingSummary)
def get_rl_training_summary(db: Session = Depends(get_db)):
    """
    Retrieve RL training progress, accumulated episode rewards, and policy stats.
    """
    return RLEngineService.get_training_summary(db)

@router.post("/recommend", response_model=RLActionRecommendation)
def recommend_rl_action(state: RLState, db: Session = Depends(get_db)):
    """
    Get RL policy recommendation for an observed building state.
    """
    return RLEngineService.recommend_action(db, state)

@router.post("/episode", response_model=RLEpisodeSummary)
def record_rl_episode(
    state: RLState,
    action: str,
    energy_saved_kwh: float,
    pmv_delta: float,
    supervisor_accepted: bool = True,
    db: Session = Depends(get_db)
):
    """
    Record an optimization cycle as an RL training episode in the SQLite database.
    """
    return RLEngineService.record_episode(
        db=db,
        state=state,
        action=action,
        energy_saved_kwh=energy_saved_kwh,
        pmv_delta=pmv_delta,
        supervisor_accepted=supervisor_accepted
    )
