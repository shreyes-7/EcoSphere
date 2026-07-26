from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.database import get_db
from backend.schemas.playback_schemas import PlaybackSession, PlaybackFrame
from backend.services.playback_service import PlaybackService

router = APIRouter(prefix="/playback", tags=["Optimization Playback System"])

@router.get("/session", response_model=PlaybackSession)
def get_playback_session(
    session_id: Optional[str] = Query(None, description="Optional playback session ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve frame-by-frame optimization timeline playback session.
    """
    return PlaybackService.get_playback_session(db, session_id=session_id)

@router.get("/frame/{index}", response_model=PlaybackFrame)
def get_playback_frame_by_index(
    index: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve specific playback frame by index number.
    """
    session = PlaybackService.get_playback_session(db)
    for frame in session.frames:
        if frame.frame_index == index:
            return frame
    raise HTTPException(status_code=404, detail=f"Playback frame index '{index}' not found.")
