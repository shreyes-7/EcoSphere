"""EnergyPlus validation and execution service."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.config import Settings, get_settings
from fastapi import Depends
from backend.utils.exceptions import (
    BuildingFileMissing,
    EnergyPlusNotFound,
    SimulationError,
    WeatherFileMissing,
)
from backend.utils.helpers import create_directory
from backend.utils.logger import get_logger


@dataclass(frozen=True)
class EnergyPlusRun:
    """Artifacts and execution metadata from one EnergyPlus process."""

    output_folder: Path
    stdout: str
    stderr: str
    exit_code: int
    execution_seconds: float


class EnergyPlusService:
    """Execute EnergyPlus with validated IDF and EPW files."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger(__name__)

    def validate_energyplus(self) -> Path:
        """Validate and return the configured EnergyPlus executable."""
        if not self._settings.energyplus_path:
            raise EnergyPlusNotFound("ENERGYPLUS_PATH is not configured")
        configured_path = Path(self._settings.energyplus_path)
        executable = configured_path / "EnergyPlus.exe" if configured_path.is_dir() else configured_path
        if not executable.is_file():
            raise EnergyPlusNotFound(f"EnergyPlus executable not found: {executable}")
        return executable

    def validate_weather(self, weather_file: str | Path) -> Path:
        """Validate a non-empty EPW weather file."""
        path = Path(weather_file)
        if not path.is_file() or path.suffix.lower() != ".epw" or path.stat().st_size == 0:
            raise WeatherFileMissing(f"Weather file missing or invalid: {path}")
        if not path.read_text(encoding="utf-8", errors="ignore")[:100].upper().startswith("LOCATION"):
            raise WeatherFileMissing(f"Weather file is corrupted: {path}")
        return path

    def validate_building(self, idf_file: str | Path) -> Path:
        """Validate a non-empty, text-based IDF building model."""
        path = Path(idf_file)
        if not path.is_file() or path.suffix.lower() != ".idf" or path.stat().st_size == 0:
            raise BuildingFileMissing(f"Building file missing or invalid: {path}")
        sample = path.read_text(encoding="utf-8", errors="ignore")[:4096].upper()
        if "VERSION" not in sample and "BUILDING" not in sample:
            raise BuildingFileMissing(f"Building file is corrupted: {path}")
        return path

    def run_simulation(
        self,
        idf_path: str | Path,
        weather_path: str | Path,
        output_folder: str | Path | None = None,
    ) -> EnergyPlusRun:
        """Run EnergyPlus and return its captured process metadata."""
        executable = self.validate_energyplus()
        building_file = self.validate_building(idf_path)
        weather_file = self.validate_weather(weather_path)
        if output_folder is None:
            run_name = datetime.now().strftime("run_%Y%m%d_%H%M%S_%f")
            output_path = self._settings.output_directory / run_name
        else:
            output_path = Path(output_folder)
        create_directory(output_path)

        command = [str(executable), "-w", str(weather_file), "-d", str(output_path), str(building_file)]
        self._logger.info("Simulation started: %s", output_path)
        started_at = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._settings.simulation_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            self._logger.exception("Simulation timed out: %s", output_path)
            raise SimulationError("EnergyPlus simulation timed out") from error
        except OSError as error:
            self._logger.exception("Simulation could not start: %s", output_path)
            raise SimulationError(f"EnergyPlus execution failed to start: {error}") from error

        execution_seconds = time.perf_counter() - started_at
        result = EnergyPlusRun(
            output_folder=output_path,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            execution_seconds=execution_seconds,
        )
        if completed.returncode != 0:
            self._logger.error("Simulation failed in %.2f seconds: %s", execution_seconds, output_path)
            raise SimulationError(
                f"EnergyPlus failed with exit code {completed.returncode}. "
                f"See {output_path / 'eplusout.err'}"
            )
        self._logger.info("Simulation finished in %.2f seconds: %s", execution_seconds, output_path)
        return result

    def read_results(self, output_folder: str | Path) -> dict[str, Any]:
        """Read parsed results from an EnergyPlus output folder."""
        from backend.services.output_parser import OutputParser

        return OutputParser().parse(Path(output_folder) / "eplusout.csv")


def get_energyplus_service(
    settings: Settings = Depends(get_settings),
) -> EnergyPlusService:
    """Create an EnergyPlus service for dependency injection."""
    return EnergyPlusService(settings)
