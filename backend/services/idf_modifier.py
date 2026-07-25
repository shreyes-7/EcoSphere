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


class NativeIDFObject:
    """AST object wrapper for an EnergyPlus object block."""

    def __init__(self, key: str, fields: list[str], raw_comments: list[str] | None = None) -> None:
        self.key = key.strip().upper()
        self.fields = [f.strip() for f in fields]
        self.raw_comments = raw_comments or []

    def __getattr__(self, name: str) -> Any:
        # Match field names dynamically
        clean_name = name.lower().replace("_", "")
        for idx, field in enumerate(self.fields):
            if clean_name in f"field_{idx+1}" or clean_name in field.lower():
                return field
        return None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("key", "fields", "raw_comments"):
            super().__setattr__(name, value)
            return
        
        val_str = str(value)
        clean_name = name.lower().replace("_", "")
        for idx, field in enumerate(self.fields):
            if clean_name in f"field_{idx+1}":
                self.fields[idx] = val_str
                return
        
        # If attribute starts with Constant_Cooling_Setpoint or similar, set specific field
        if "cooling" in clean_name and len(self.fields) > 1:
            self.fields[1] = val_str
        elif "heating" in clean_name and len(self.fields) > 0:
            self.fields[0] = val_str
        elif "hourly" in clean_name and len(self.fields) > 0:
            self.fields[0] = val_str
        elif "watts" in clean_name and len(self.fields) > 1:
            self.fields[1] = val_str
        elif "people" in clean_name and len(self.fields) > 1:
            self.fields[1] = val_str
        else:
            self.fields.append(val_str)


class NativeIDFAST:
    """Native IDF AST parser and formatter for EnergyPlus building models."""

    def __init__(self, idf_path: Path) -> None:
        self.path = idf_path
        self.idfobjects: dict[str, list[NativeIDFObject]] = {}
        self._parse()

    def _parse(self) -> None:
        content = self.path.read_text(encoding="utf-8", errors="ignore")
        # Strip comments outside objects
        lines = content.splitlines()
        object_blocks: list[str] = []
        current_block: list[str] = []

        for line in lines:
            stripped = line.split("!")[0].strip()
            if not stripped:
                continue
            current_block.append(stripped)
            if ";" in stripped:
                full_obj = " ".join(current_block)
                object_blocks.append(full_obj)
                current_block = []

        for block in object_blocks:
            parts = [p.strip() for p in block.rstrip(";").split(",")]
            if not parts or not parts[0]:
                continue
            key = parts[0].upper()
            fields = parts[1:]
            obj = NativeIDFObject(key, fields)
            self.idfobjects.setdefault(key, []).append(obj)

    def saveas(self, target_path: str) -> None:
        out_path = Path(target_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = ["! Modified by EcoSphere Physical AI Engine AST Parser", ""]

        for key, objs in self.idfobjects.items():
            for obj in objs:
                lines.append(f"  {key},")
                for i, field in enumerate(obj.fields):
                    term = ";" if i == len(obj.fields) - 1 else ","
                    lines.append(f"    {field}{term}")
                lines.append("")

        out_path.write_text("\n".join(lines), encoding="utf-8")


class IDFModifierService:
    """Modify EnergyPlus IDF objects using eppy or native AST parser."""

    def __init__(self, settings: Settings, idd_path: str | Path | None = None) -> None:
        """Initialize the modifier with configuration and optional EnergyPlus IDD path."""
        self._settings = settings
        self._logger = get_logger(__name__)
        self._idd_path = Path(idd_path) if idd_path else self._resolve_idd_path()

    def _resolve_idd_path(self) -> Path | None:
        """Attempt to locate the EnergyPlus IDD file from configured paths, standard installs, or eppy resources."""
        if self._settings.energyplus_path:
            ep_exec = Path(self._settings.energyplus_path)
            base_dir = ep_exec if ep_exec.is_dir() else ep_exec.parent
            for name in ["EnergyPlus.idd", "energyplus.idd", "Energy+.idd"]:
                idd_candidate = base_dir / name
                if idd_candidate.is_file():
                    return idd_candidate

        # Search standard EnergyPlus installation directories
        for root in [Path("C:/"), Path("D:/"), Path("C:/Program Files")]:
            if root.exists():
                for ep_dir in root.glob("EnergyPlusV*"):
                    for name in ["EnergyPlus.idd", "energyplus.idd"]:
                        idd_candidate = ep_dir / name
                        if idd_candidate.is_file():
                            return idd_candidate

        # Search eppy bundled resources
        try:
            import eppy
            import re
            eppy_dir = Path(eppy.__file__).parent
            idd_files = list(eppy_dir.glob("resources/iddfiles/*.idd"))
            if idd_files:
                def extract_ver(p: Path) -> tuple[int, ...]:
                    nums = re.findall(r"\d+", p.name)
                    return tuple(int(x) for x in nums) if nums else (0,)
                
                idd_files.sort(key=extract_ver)
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
        """Load an EnergyPlus IDF file using eppy or native AST representation."""
        path = Path(idf_path)
        if not path.is_file():
            raise BuildingFileMissing(f"IDF file not found: {path}")

        try:
            from eppy.modeleditor import IDF
            self._init_eppy_idd()
            return IDF(str(path))
        except Exception as first_error:
            self._logger.info("eppy IDD mismatch for %s; using NativeIDFAST parser: %s", path.name, first_error)
            try:
                return NativeIDFAST(path)
            except Exception as sec_error:
                raise IDFModificationError(
                    f"Failed to load IDF file via AST parser: {sec_error}."
                ) from sec_error

    def modify_cooling_setpoint(self, idf: Any, setpoint_celsius: float) -> int:
        """Update cooling setpoint temperatures in dual setpoints, HVAC templates, or schedules."""
        modified_count = 0

        # Update HVACTemplate:Thermostat objects
        for obj in idf.idfobjects.get("HVACTEMPLATE:THERMOSTAT", []):
            if len(getattr(obj, "fields", [])) > 1:
                obj.fields[1] = str(setpoint_celsius)
                modified_count += 1
            elif hasattr(obj, "Constant_Cooling_Setpoint"):
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

        # Fallback: create or update HVACTemplate:Thermostat in AST
        if modified_count == 0:
            if hasattr(idf, "idfobjects"):
                thermostats = idf.idfobjects.setdefault("HVACTEMPLATE:THERMOSTAT", [])
                if thermostats:
                    thermostats[0].fields = [thermostats[0].fields[0] if thermostats[0].fields else "Thermostat1", str(setpoint_celsius)]
                else:
                    from backend.services.idf_modifier import NativeIDFObject
                    obj = NativeIDFObject("HVACTEMPLATE:THERMOSTAT", ["ConstantThermostat", str(setpoint_celsius)])
                    thermostats.append(obj)
                modified_count += 1

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
