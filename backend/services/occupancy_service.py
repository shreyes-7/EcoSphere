import datetime
from typing import List, Dict, Any, Optional
from backend.schemas.occupancy_schemas import ZoneOccupancyProfile, BuildingOccupancySummary

DEFAULT_OCCUPANCY_DATA = [
    {"zone_id": "zone_101", "name": "Main Open Office", "state": "Occupied", "priority": "Normal", "current_occupants": 18, "max_capacity": 25, "scheduled_next": "17:00 (Vacant)"},
    {"zone_id": "zone_102", "name": "Executive Conference", "state": "Reserved", "priority": "Critical", "current_occupants": 0, "max_capacity": 12, "scheduled_next": "10:00 (Meeting)"},
    {"zone_id": "zone_103", "name": "Server & IT Hub", "state": "Vacant", "priority": "Critical", "current_occupants": 0, "max_capacity": 4, "scheduled_next": "24/7 Operational"},
    {"zone_id": "zone_104", "name": "South Perimeter Workspaces", "state": "Occupied", "priority": "Normal", "current_occupants": 12, "max_capacity": 20, "scheduled_next": "18:00 (Closed)"},
    {"zone_id": "zone_105", "name": "North Quiet Zone", "state": "Partially Occupied", "priority": "Low", "current_occupants": 3, "max_capacity": 15, "scheduled_next": "14:00 (Occupied)"},
    {"zone_id": "zone_106", "name": "Cafeteria & Lounge", "state": "Vacant", "priority": "Unused", "current_occupants": 0, "max_capacity": 40, "scheduled_next": "12:00 (Lunch Peak)"},
]

class OccupancyService:
    """
    Service providing real-time zone occupancy tracking, zone priority evaluation,
    pre-conditioning schedules, post-occupancy recovery, and HVAC energy waste detection.
    """

    @classmethod
    def get_building_occupancy_summary(cls, building_name: str = "Commercial Test Facility") -> BuildingOccupancySummary:
        profiles: List[ZoneOccupancyProfile] = []
        occupied_count = 0
        vacant_count = 0
        total_waste_kw = 0.0
        warnings: List[str] = []

        for item in DEFAULT_OCCUPANCY_DATA:
            is_occupied = item["state"] in ["Occupied", "Partially Occupied"]
            is_vacant = item["state"] in ["Vacant", "Closed"]

            if is_occupied:
                occupied_count += 1
            elif is_vacant:
                vacant_count += 1

            # Energy Waste Detection: HVAC running in vacant low/unused priority zones
            waste_detected = False
            waste_kw = 0.0
            if is_vacant and item["priority"] in ["Unused", "Low"]:
                waste_detected = True
                waste_kw = 8.5
                total_waste_kw += waste_kw
                warnings.append(f"Energy Waste Warning: Cooling active in vacant '{item['name']}' ({waste_kw} kW wasted)")

            # Pre-conditioning active for Reserved zones
            pre_conditioning = item["state"] == "Reserved"

            profile = ZoneOccupancyProfile(
                zone_id=item["zone_id"],
                name=item["name"],
                state=item["state"],
                priority=item["priority"],
                current_occupants=item["current_occupants"],
                max_capacity=item["max_capacity"],
                scheduled_next_occupancy=item["scheduled_next"],
                pre_conditioning_active=pre_conditioning,
                hvac_waste_detected=waste_detected,
                energy_waste_kw=waste_kw
            )
            profiles.append(profile)

        total_zones = len(profiles)
        compliance_pct = round(((total_zones - len(warnings)) / total_zones) * 100.0, 1) if total_zones > 0 else 100.0

        return BuildingOccupancySummary(
            building_name=building_name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            total_occupied_zones=occupied_count,
            total_vacant_zones=vacant_count,
            total_wasted_energy_kw=round(total_waste_kw, 2),
            occupancy_compliance_pct=compliance_pct,
            zones=profiles,
            energy_waste_warnings=warnings
        )
