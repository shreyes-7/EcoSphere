from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.database import get_db
from backend.schemas.digital_twin_schemas import BuildingDigitalTwinState, HeatmapData, ZoneMetric
from backend.services.digital_twin_service import DigitalTwinService

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin & Heatmap"])

@router.get("/state", response_model=BuildingDigitalTwinState)
def get_digital_twin_state(
    simulation_id: Optional[int] = Query(None, description="Optional simulation ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve real-time building Digital Twin state and zone metrics.
    """
    return DigitalTwinService.get_building_digital_twin_state(db, simulation_id=simulation_id)

@router.get("/heatmap", response_model=HeatmapData)
def get_heatmap_data(
    mode: str = Query("temperature", description="Heatmap mode: temperature | energy | comfort | carbon"),
    simulation_id: Optional[int] = Query(None, description="Optional simulation ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve spatial heatmap values across building thermal zones.
    """
    return DigitalTwinService.get_heatmap_data(db, mode=mode, simulation_id=simulation_id)

@router.get("/zone/{zone_id}", response_model=ZoneMetric)
def get_zone_details(
    zone_id: str,
    simulation_id: Optional[int] = Query(None, description="Optional simulation ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieve detailed metrics and agent recommendations for a specific thermal zone.
    """
    state = DigitalTwinService.get_building_digital_twin_state(db, simulation_id=simulation_id)
    for z in state.zones:
        if z.zone_id == zone_id:
            return z
    raise HTTPException(status_code=404, detail=f"Thermal zone '{zone_id}' not found.")
