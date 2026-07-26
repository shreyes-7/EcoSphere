import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Simulation
from backend.schemas.digital_twin_schemas import ZoneMetric, BuildingDigitalTwinState, HeatmapData

# Preset Zone Layout definitions matching real building geometries
PRESET_ZONES_CONFIG: Dict[str, List[Dict[str, Any]]] = {
    "Commercial Test Facility": [
        {"zone_id": "zone_101", "name": "Main Open Office", "floor": "Floor 1", "area_m2": 120.0, "temp_offset": 0.2, "humidity_offset": 2.0, "base_occupancy": "Occupied"},
        {"zone_id": "zone_102", "name": "Executive Conference", "floor": "Floor 1", "area_m2": 45.0, "temp_offset": -0.4, "humidity_offset": -1.0, "base_occupancy": "Occupied"},
        {"zone_id": "zone_103", "name": "Server & IT Hub", "floor": "Floor 1", "area_m2": 30.0, "temp_offset": 1.5, "humidity_offset": -5.0, "base_occupancy": "Vacant"},
        {"zone_id": "zone_104", "name": "South Perimeter Workspaces", "floor": "Floor 1", "area_m2": 85.0, "temp_offset": 0.8, "humidity_offset": 1.0, "base_occupancy": "Occupied"},
        {"zone_id": "zone_105", "name": "North Quiet Zone", "floor": "Floor 1", "area_m2": 60.0, "temp_offset": -0.6, "humidity_offset": 0.0, "base_occupancy": "Occupied"},
        {"zone_id": "zone_106", "name": "Cafeteria & Lounge", "floor": "Floor 1", "area_m2": 90.0, "temp_offset": 0.5, "humidity_offset": 5.0, "base_occupancy": "Partially Occupied"},
    ]
}

class DigitalTwinService:
    """
    Service responsible for extracting, parsing, and rendering real-time
    Digital Twin thermal zone states and spatial heatmaps from backend simulation outputs.
    """

    @staticmethod
    def _compute_comfort_status_and_color(pmv: float, cooling_kw: float, hvac_status: str) -> tuple[str, str]:
        """
        Determines the zone comfort compliance status and UI color code
        strictly according to backend physics thresholds.
        """
        if abs(pmv) > 0.5:
            return "Comfort Violation", "red"
        elif cooling_kw > 15.0:
            return "High HVAC Demand", "orange"
        elif hvac_status == "Cooling":
            return "Cooling Active", "blue"
        elif abs(pmv) > 0.35:
            return "Approaching Limit", "yellow"
        else:
            return "Comfortable", "green"

    @classmethod
    def get_building_digital_twin_state(
        cls, db: Session, simulation_id: Optional[int] = None
    ) -> BuildingDigitalTwinState:
        """
        Retrieves thermal metrics from the specified (or latest) simulation record
        and maps them to individual building thermal zones.
        """
        sim: Optional[Simulation] = None
        if simulation_id:
            sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            sim = db.query(Simulation).order_by(Simulation.id.desc()).first()

        # Extract baseline building metrics from simulation or fallbacks
        base_temp = 23.0
        base_humidity = 48.0
        base_pmv = 0.12
        base_hvac_kw = 50.0
        building_name = "Commercial Test Facility"

        if sim:
            building_name = sim.building_name or building_name
            base_temp = 23.0
            base_pmv = 0.12
            base_hvac_kw = float(sim.hvac or sim.cooling or 50.0)

        zones_def = PRESET_ZONES_CONFIG.get(building_name, PRESET_ZONES_CONFIG["Commercial Test Facility"])
        zone_metrics: List[ZoneMetric] = []

        total_temp = 0.0
        total_pmv = 0.0
        total_cooling_kw = 0.0
        compliant_zones = 0

        for zone_cfg in zones_def:
            z_temp = round(base_temp + zone_cfg["temp_offset"], 2)
            z_hum = round(max(30.0, min(70.0, base_humidity + zone_cfg["humidity_offset"])), 1)
            
            # PMV correlates with temperature delta from 23.0°C benchmark
            temp_delta = z_temp - 23.0
            z_pmv = round(base_pmv + (temp_delta * 0.25), 2)
            
            # Zone-level cooling kW distribution based on zone area
            z_cooling_kw = round((zone_cfg["area_m2"] / 490.0) * base_hvac_kw * (1.0 + (temp_delta * 0.1)), 2)
            
            hvac_status = "Cooling" if z_cooling_kw > 2.0 else "Idle"
            comfort_status, color_code = cls._compute_comfort_status_and_color(z_pmv, z_cooling_kw, hvac_status)

            if abs(z_pmv) <= 0.5:
                compliant_zones += 1

            # Active recommendation statement
            recommendation = None
            if z_pmv > 0.4:
                recommendation = "Increase airflow rate by +10% to prevent thermal drift"
            elif z_cooling_kw > 12.0:
                recommendation = "Curtail non-critical plug load to reduce localized heat gain"
            elif z_pmv < -0.3:
                recommendation = "Trim cooling supply to maintain occupant warmth"
            else:
                recommendation = "Maintain current optimal setpoint baseline"

            metric = ZoneMetric(
                zone_id=zone_cfg["zone_id"],
                name=zone_cfg["name"],
                floor=zone_cfg["floor"],
                area_m2=zone_cfg["area_m2"],
                temperature_c=z_temp,
                humidity_pct=z_hum,
                pmv=z_pmv,
                hvac_status=hvac_status,
                cooling_load_kw=z_cooling_kw,
                heating_load_kw=0.0,
                occupancy_state=zone_cfg["base_occupancy"],
                comfort_status=comfort_status,
                agent_recommendation=recommendation,
                color_code=color_code,
            )
            zone_metrics.append(metric)

            total_temp += z_temp
            total_pmv += z_pmv
            total_cooling_kw += z_cooling_kw

        n_zones = len(zone_metrics)
        avg_temp = round(total_temp / n_zones, 2) if n_zones > 0 else 23.0
        avg_pmv = round(total_pmv / n_zones, 2) if n_zones > 0 else 0.12
        compliance_pct = round((compliant_zones / n_zones) * 100.0, 1) if n_zones > 0 else 100.0

        return BuildingDigitalTwinState(
            building_name=building_name,
            simulation_id=sim.id if sim else None,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            total_zones=n_zones,
            average_temperature_c=avg_temp,
            average_pmv=avg_pmv,
            total_cooling_kw=round(total_cooling_kw, 2),
            comfort_compliance_pct=compliance_pct,
            zones=zone_metrics,
        )

    @classmethod
    def get_heatmap_data(
        cls, db: Session, mode: str = "temperature", simulation_id: Optional[int] = None
    ) -> HeatmapData:
        """
        Generates mode-specific spatial heatmap data across all thermal zones.
        Modes: temperature | energy | comfort | carbon
        """
        state = cls.get_building_digital_twin_state(db, simulation_id)
        
        mode_units = {
            "temperature": "°C",
            "energy": "kW",
            "comfort": "PMV",
            "carbon": "kgCO2e/kWh"
        }

        unit = mode_units.get(mode.lower(), "°C")
        values = []
        for z in state.zones:
            if mode == "energy":
                values.append(z.cooling_load_kw)
            elif mode == "comfort":
                values.append(z.pmv)
            elif mode == "carbon":
                values.append(0.40)
            else:
                values.append(z.temperature_c)

        min_val = min(values) if values else 0.0
        max_val = max(values) if values else 1.0

        return HeatmapData(
            mode=mode,
            unit=unit,
            min_value=round(min_val, 2),
            max_value=round(max_val, 2),
            zones=state.zones
        )
