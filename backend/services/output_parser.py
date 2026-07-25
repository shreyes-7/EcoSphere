"""Parser for EnergyPlus CSV output files."""

from __future__ import annotations

import csv
from pathlib import Path

from backend.utils.exceptions import SimulationError


class OutputParser:
    """Extract energy totals from common EnergyPlus CSV output variables."""

    _METRIC_PATTERNS = {
        "electricity": ("electricity:facility",),
        "cooling": ("cooling:energytransfer", "districtcooling:facility", "cooling:electricity"),
        "heating": ("heating:energytransfer", "districtheating:facility", "heating:electricity"),
        "fans": ("fan:fan electricity", "fans:electricity"),
        "pumps": ("pump:pump electricity", "pumps:electricity"),
        "interior_lights": ("interiorlights:electricity", "lights:interior"),
    }

    def parse(self, csv_path: str | Path) -> dict[str, float]:
        """Parse a CSV and return energy totals in kWh when units are joules."""
        path = Path(csv_path)
        if not path.is_file() or path.stat().st_size == 0:
            raise SimulationError(f"EnergyPlus output CSV is missing: {path}")

        totals = {metric: 0.0 for metric in self._METRIC_PATTERNS}
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                if not reader.fieldnames:
                    raise SimulationError("EnergyPlus output CSV has no headers")
                matched_columns = self._matched_columns(reader.fieldnames)
                for row in reader:
                    for metric, columns in matched_columns.items():
                        for column in columns:
                            value = self._to_float(row.get(column))
                            if value is not None:
                                totals[metric] += self._to_kwh(value, column)
        except OSError as error:
            raise SimulationError(f"Unable to read EnergyPlus output CSV: {error}") from error

        electricity = totals["electricity"]
        hvac = totals["cooling"] + totals["heating"] + totals["fans"] + totals["pumps"]
        return {
            "electricity": round(electricity, 3),
            "cooling": round(totals["cooling"], 3),
            "heating": round(totals["heating"], 3),
            "hvac": round(hvac, 3),
            "interior_lights": round(totals["interior_lights"], 3),
            "fans": round(totals["fans"], 3),
            "pumps": round(totals["pumps"], 3),
        }

    def _matched_columns(self, headers: list[str]) -> dict[str, list[str]]:
        """Map output headers to requested metrics."""
        return {
            metric: [header for header in headers if any(pattern in header.lower() for pattern in patterns)]
            for metric, patterns in self._METRIC_PATTERNS.items()
        }

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        """Convert a CSV value to float, ignoring missing or malformed cells."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _to_kwh(value: float, header: str) -> float:
        """Convert joule-based EnergyPlus values to kWh; preserve kWh values."""
        return value / 3_600_000 if "[j]" in header.lower() else value
