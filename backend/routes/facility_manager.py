from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.schemas.facility_manager_schemas import FacilityManagerRequest, FacilityManagerResponse
from backend.services.facility_manager_service import FacilityManagerService

router = APIRouter(prefix="/facility-manager", tags=["AI Facility Manager"])

@router.post("/chat", response_model=FacilityManagerResponse)
async def facility_manager_chat(
    request: FacilityManagerRequest,
    db: Session = Depends(get_db)
):
    """
    Conversational AI Facility Manager interface with tool calling and multi-turn context awareness.
    """
    return await FacilityManagerService.process_chat(db, request)
