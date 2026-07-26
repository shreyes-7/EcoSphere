from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.self_healing_schemas import BuildingHealthScore, IncidentRecord
from backend.services.self_healing_service import SelfHealingService

router = APIRouter(prefix="/self-healing", tags=["Self-Healing Building Engine"])

@router.get("/health", response_model=BuildingHealthScore)
def get_building_health(db: Session = Depends(get_db)):
    """
    Retrieve real-time Building Health Score, active incidents, and automated recovery metrics.
    """
    return SelfHealingService.calculate_building_health(db)

@router.post("/resolve/{incident_id}", response_model=IncidentRecord)
def resolve_building_incident(incident_id: str, db: Session = Depends(get_db)):
    """
    Trigger automated recovery execution for a building incident.
    """
    return SelfHealingService.resolve_incident(db, incident_id)
