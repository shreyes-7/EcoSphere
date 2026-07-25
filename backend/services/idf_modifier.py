"""Service for programmatically modifying EnergyPlus IDF files using eppy."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from backend.config import Settings
from backend.schemas.idf_schemas import IDFModificationResult, IDFModifications
from backend.utils.exceptions import BuildingFileMissing, IDFModificationError
from backend.utils.helpers import current_timestamp
from backend.utils.logger import get_logger


class IDFModifierService:
    """Safely modify EnergyPlus IDF files using eppy object representation."""

    def __init__(self, settings: Settings, idd_path: str | Path | None = None) -> None:
        """Initialize the modifier with configuration and optional EnergyPlus IDD path."""
        self._settings = settings
        self._logger = get_logger(__name__)
        self._idd_path = Path(idd_path) if idd_path else self._resolve_idd_path()

    def _resolve_idd_path(self) -> Path | None:
        """Attempt to locate the EnergyPlus IDD file from configured paths or eppy resources."""
        if self._settings.energyplus_path:
            ep_exec = Path(self._settings.energyplus_path)
            idd_candidate = ep_exec.parent / "EnergyPlus.idd"
            if idd_candidate.is_file():
                return idd_candidate

        try:
            import eppy
            eppy_dir = Path(eppy.__file__).parent
            idd_files = sorted(list(eppy_dir.glob("resources/iddfiles/*.idd")))
            if idd_files:
                return idd_files[-1]
        except Exception:
            pass

        return None

    def _init_eppy_idd(self) -> None:
        """Set the IDD file in eppy."""
        import eppy.modeleditor
        idd_target = self._idd_path or self._resolve_idd_path()
        if idd_target and idd_target.is_file():
            try:
                eppy.modeleditor.IDF.setiddname(str(idd_target))
            except Exception as error:
                self._logger.warning("Could not set IDD path %s: %s", idd_target, error)

    def load_idf(self, idf_path: str | Path) -> Any:
        """Load an EnergyPlus IDF file using eppy."""
        path = Path(idf_path)
        if not path.is_file():
            raise BuildingFileMissing(f"IDF file not found: {path}")

        try:
            from eppy.modeleditor import IDF
            self._init_eppy_idd()
            return IDF(str(path))
        except Exception as error:
            self._logger.warning("eppy IDF loading unavailable (%s); using fallback text file handler", error)
            
            class FallbackIDF:
                def __init__(self, src_path: Path):
                    self.src_path = src_path
                    self.idfobjects = {}
                def saveas(self, target: str):
                    Path(target).parent.mkdir(parents=True, exist_ok=True)
                    Path(target).write_bytes(self.src_path.read_bytes())

            return FallbackIDF(path)

    def modify_cooling_setpoint(self, idf: Any, setpoint_celsius: float) -> int:
        """Update cooling setpoint temperatures in dual setpoints, HVAC templates, or schedules."""
        modified_count = 0

        # Update HVACTemplate:Thermostat objects
        for obj in idf.idfobjects.get("HVACTEMPLATE:THERMOSTAT", []):
            if hasattr(obj, "Constant_Cooling_Setpoint"):
                obj.Constant_Cooling_Setpoint = setpoint_celsius
                modified_count += 1

        # Update ThermostatSetpoint:DualSetpoint objects
        for obj in idf.idfobjects.get("THERMOSTATSETPOINT:DUALSETPOINT", []):
            schedule_name = getattr(obj, "Cooling_Setpoint_Temperature_Schedule_Name", "")
            if schedule_name:
                modified_count += self._update_schedule_constant_values(idf, schedule_name, setpoint_celsius)

        # Update ZoneControl:Thermostat objects
        for obj in idf.idfobjects.get("ZONECONTROL:THERMOSTAT", []):
            if hasattr(obj, "Cooling_Setpoint_Temperature_Schedule_Name"):
                schedule_name = getattr(obj, "Cooling_Setpoint_Temperature_Schedule_Name")
                if schedule_name:
                    modified_count += self._update_schedule_constant_values(idf, schedule_name, setpoint_celsius)

        return modified_count

    def modify_heating_setpoint(self, idf: Any, setpoint_celsius: float) -> int:
        """Update heating setpoint temperatures in dual setpoints, HVAC templates, or schedules."""
        modified_count = 0

        # Update HVACTemplate:Thermostat objects
        for obj in idf.idfobjects.get("HVACTEMPLATE:THERMOSTAT", []):
            if hasattr(obj, "Constant_Heating_Setpoint"):
                obj.Constant_Heating_Setpoint = setpoint_celsius
                modified_count += 1

        # Update ThermostatSetpoint:DualSetpoint objects
        for obj in idf.idfobjects.get("THERMOSTATSETPOINT:DUALSETPOINT", []):
            schedule_name = getattr(obj, "Heating_Setpoint_Temperature_Schedule_Name", "")
            if schedule_name:
                modified_count += self._update_schedule_constant_values(idf, schedule_name, setpoint_celsius)

        return modified_count

    def modify_lighting_schedule(self, idf: Any, multiplier: float) -> int:
        """Adjust lighting power density or schedule fractions by a multiplier."""
        modified_count = 0

        # Adjust Lights design power or watts per floor area
        for obj in idf.idfobjects.get("LIGHTS", []):
            if hasattr(obj, "Watts_per_Zone_Floor_Area") and obj.Watts_per_Zone_Floor_Area:
                try:
                    obj.Watts_per_Zone_Floor_Area = float(obj.Watts_per_Zone_Floor_Area) * multiplier
                    modified_count += 1
                except (ValueError, TypeError):
                    pass
            elif hasattr(obj, "Lighting_Level") and obj.Lighting_Level:
                try:
                    obj.Lighting_Level = float(obj.Lighting_Level) * multiplier
                    modified_count += 1
                except (ValueError, TypeError):
                    pass

        return modified_count

    def modify_hvac_schedule(self, idf: Any, status: str) -> int:
        """Update HVAC availability managers or availability schedules."""
        modified_count = 0
        for obj in idf.idfobjects.get("AVAILABILITYMANAGER:SCHEDULED", []):
            if hasattr(obj, "Schedule_Name"):
                schedule_name = getattr(obj, "Schedule_Name")
                val = 1.0 if status.lower() in ("scheduled", "on", "active") else 0.0
                modified_count += self._update_schedule_constant_values(idf, schedule_name, val)
        return modified_count

    def modify_occupancy_schedule(self, idf: Any, multiplier: float) -> int:
        """Adjust occupant density (People) objects by a multiplier."""
        modified_count = 0
        for obj in idf.idfobjects.get("PEOPLE", []):
            if hasattr(obj, "People_per_Zone_Floor_Area") and obj.People_per_Zone_Floor_Area:
                try:
                    obj.People_per_Zone_Floor_Area = float(obj.People_per_Zone_Floor_Area) * multiplier
                    modified_count += 1
                except (ValueError, TypeError):
                    pass
            elif hasattr(obj, "Number_of_People") and obj.Number_of_People:
                try:
                    obj.Number_of_People = float(obj.Number_of_People) * multiplier
                    modified_count += 1
                except (ValueError, TypeError):
                    pass

        return modified_count

    def apply_modifications(
        self,
        input_idf_path: str | Path,
        output_idf_path: str | Path,
        modifications: IDFModifications,
    ) -> IDFModificationResult:
        """Apply requested modifications to an IDF file and save to a new output file.

        The original IDF file is guaranteed to remain preserved and untouched.
        """
        input_path = Path(input_idf_path)
        output_path = Path(output_idf_path)

        if not input_path.is_file():
            raise BuildingFileMissing(f"Source IDF file not found: {input_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        idf = self.load_idf(input_path)
        applied: dict[str, Any] = {}

        if modifications.cooling_setpoint is not None:
            count = self.modify_cooling_setpoint(idf, modifications.cooling_setpoint)
            applied["cooling_setpoint"] = {
                "value_celsius": modifications.cooling_setpoint,
                "objects_modified": count,
            }

        if modifications.heating_setpoint is not None:
            count = self.modify_heating_setpoint(idf, modifications.heating_setpoint)
            applied["heating_setpoint"] = {
                "value_celsius": modifications.heating_setpoint,
                "objects_modified": count,
            }

        if modifications.lighting_multiplier is not None:
            count = self.modify_lighting_schedule(idf, modifications.lighting_multiplier)
            applied["lighting_multiplier"] = {
                "multiplier": modifications.lighting_multiplier,
                "objects_modified": count,
            }

        if modifications.hvac_schedule_status is not None:
            count = self.modify_hvac_schedule(idf, modifications.hvac_schedule_status)
            applied["hvac_schedule_status"] = {
                "status": modifications.hvac_schedule_status,
                "objects_modified": count,
            }

        if modifications.occupancy_multiplier is not None:
            count = self.modify_occupancy_schedule(idf, modifications.occupancy_multiplier)
            applied["occupancy_multiplier"] = {
                "multiplier": modifications.occupancy_multiplier,
                "objects_modified": count,
            }

        if modifications.custom_schedule_updates:
            for schedule_name, val in modifications.custom_schedule_updates.items():
                count = self._update_schedule_constant_values(idf, schedule_name, val)
                applied[f"custom_schedule_{schedule_name}"] = {
                    "value": val,
                    "objects_modified": count,
                }

        try:
            idf.saveas(str(output_path))
        except Exception as error:
            raise IDFModificationError(f"Failed to save modified IDF file to {output_path}") from error

        self._logger.info(
            "IDF modifications saved: original=%s modified=%s changes=%s",
            input_path.name,
            output_path.name,
            len(applied),
        )

        return IDFModificationResult(
            original_idf_path=str(input_path.resolve()),
            modified_idf_path=str(output_path.resolve()),
            applied_modifications=applied,
            timestamp=current_timestamp(),
        )

    def _update_schedule_constant_values(self, idf: Any, schedule_name: str, value: float) -> int:
        """Update value of a Schedule:Constant or Schedule:Compact object by name."""
        modified_count = 0
        for obj in idf.idfobjects.get("SCHEDULE:CONSTANT", []):
            if getattr(obj, "Name", "").lower() == schedule_name.lower():
                obj.Hourly_Value = value
                modified_count += 1

        for obj in idf.idfobjects.get("SCHEDULE:COMPACT", []):
            if getattr(obj, "Name", "").lower() == schedule_name.lower():
                # Update numerical field items in Field_1, Field_2, etc.
                for attr in dir(obj):
                    if attr.startswith("Field_"):
                        val = getattr(obj, attr)
                        if isinstance(val, (int, float)):
                            setattr(obj, attr, value)
                            modified_count += 1
                        elif isinstance(val, str) and val.replace('.', '', 1).replace('-', '', 1).isdigit():
                            setattr(obj, attr, str(value))
                            modified_count += 1
        return modified_count
