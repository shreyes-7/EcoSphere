from fastapi import APIRouter, Query, HTTPException
from backend.schemas.occupancy_schemas import BuildingOccupancySummary, ZoneOccupancyProfile
from backend.services.occupancy_service import OccupancyService

router = APIRouter(prefix="/occupancy", tags=["Occupancy Engine"])

@router.get("/summary", response_model=BuildingOccupancySummary)
def get_occupancy_summary(
    building_name: str = Query("Commercial Test Facility", description="Building name")
):
    """
    Retrieve real-time occupancy profile, zone priorities, and energy waste detection.
    """
    return OccupancyService.get_building_occupancy_summary(building_name=building_name)

@router.get("/zone/{zone_id}", response_model=ZoneOccupancyProfile)
def get_zone_occupancy(zone_id: str):
    """
    Retrieve occupancy profile for a specific thermal zone.
    """
    summary = OccupancyService.get_building_occupancy_summary()
    for z in summary.zones:
        if z.zone_id == zone_id:
            return z
    raise HTTPException(status_code=404, detail=f"Zone occupancy profile for '{zone_id}' not found.")
