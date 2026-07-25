"""Comprehensive parser for EnergyPlus output files (CSV, HTML, SQL)."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from backend.utils.exceptions import SimulationError


class OutputParser:
    """Extract energy totals, thermal comfort metrics, and zone environmental metrics from EnergyPlus output files."""

    _SUM_PATTERNS = {
        "electricity": ("electricity:facility", "electricity:building"),
        "cooling": ("cooling:energytransfer", "districtcooling:facility", "cooling:electricity", "chiller electricity"),
        "heating": ("heating:energytransfer", "districtheating:facility", "heating:electricity", "boiler naturalgas"),
        "fans": ("fan:fan electricity", "fans:electricity", "fan electricity"),
        "pumps": ("pump:pump electricity", "pumps:electricity", "pump electricity"),
        "interior_lights": ("interiorlights:electricity", "lights:interior", "interior lights electricity"),
    }

    _AVG_PATTERNS = {
        "indoor_temperature": ("zone mean air temperature", "zone air temperature"),
        "relative_humidity": ("zone air relative humidity", "zone relative humidity"),
        "pmv": ("zone thermal comfort fanger model pmv", "fanger pmv", "pmv"),
        "occupancy": ("zone people occupant count", "people occupant count"),
        "outdoor_temperature": ("site outdoor air drybulb temperature", "outdoor drybulb"),
    }

    _PEAK_PATTERNS = {
        "peak_demand_kw": ("facility total electric demand power", "facility total electricity demand rate"),
    }

    def parse(self, csv_path: str | Path) -> dict[str, Any]:
        """Parse eplusout.csv and return energy totals (kWh), average temperatures (°C), PMV, humidity (%), and peak kW."""
        path = Path(csv_path)
        if not path.is_file() or path.stat().st_size == 0:
            raise SimulationError(f"EnergyPlus output CSV is missing: {path}")

        sum_totals = {metric: 0.0 for metric in self._SUM_PATTERNS}
        avg_sums = {metric: 0.0 for metric in self._AVG_PATTERNS}
        avg_counts = {metric: 0 for metric in self._AVG_PATTERNS}
        peak_values = {metric: 0.0 for metric in self._PEAK_PATTERNS}

        try:
            with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                if not reader.fieldnames:
                    raise SimulationError("EnergyPlus output CSV has no headers")

                matched_sum_cols = self._match_columns(reader.fieldnames, self._SUM_PATTERNS)
                matched_avg_cols = self._match_columns(reader.fieldnames, self._AVG_PATTERNS)
                matched_peak_cols = self._match_columns(reader.fieldnames, self._PEAK_PATTERNS)

                for row in reader:
                    # Process energy sum metrics
                    for metric, columns in matched_sum_cols.items():
                        for column in columns:
                            value = self._to_float(row.get(column))
                            if value is not None:
                                sum_totals[metric] += self._to_kwh(value, column)

                    # Process environmental averages
                    for metric, columns in matched_avg_cols.items():
                        for column in columns:
                            value = self._to_float(row.get(column))
                            if value is not None:
                                avg_sums[metric] += value
                                avg_counts[metric] += 1

                    # Process peak electric demand kW
                    for metric, columns in matched_peak_cols.items():
                        for column in columns:
                            value = self._to_float(row.get(column))
                            if value is not None:
                                kw_val = value / 1000.0 if "[w]" in column.lower() else value
                                if kw_val > peak_values[metric]:
                                    peak_values[metric] = kw_val

        except OSError as error:
            raise SimulationError(f"Unable to read EnergyPlus output CSV: {error}") from error

        electricity = sum_totals["electricity"]
        hvac = sum_totals["cooling"] + sum_totals["heating"] + sum_totals["fans"] + sum_totals["pumps"]
        total_energy = electricity if electricity > 0 else (hvac + sum_totals["interior_lights"])

        results: dict[str, Any] = {
            "electricity": round(electricity, 3),
            "cooling": round(sum_totals["cooling"], 3),
            "heating": round(sum_totals["heating"], 3),
            "hvac": round(hvac, 3),
            "interior_lights": round(sum_totals["interior_lights"], 3),
            "fans": round(sum_totals["fans"], 3),
            "pumps": round(sum_totals["pumps"], 3),
            "total_energy": round(total_energy, 3),
        }

        # Calculate averages
        for metric in self._AVG_PATTERNS:
            if avg_counts[metric] > 0:
                results[metric] = round(avg_sums[metric] / avg_counts[metric], 2)
            else:
                results[metric] = None

        # Add peak demand kW
        results["peak_demand_kw"] = round(peak_values["peak_demand_kw"], 2) if peak_values["peak_demand_kw"] > 0 else None

        # Try parsing eplusout.htm if present for additional verification
        htm_path = path.parent / "eplusout.htm"
        if htm_path.is_file():
            htm_data = self.parse_html_summary(htm_path)
            for k, v in htm_data.items():
                if results.get(k) is None or (isinstance(results.get(k), float) and results[k] == 0.0 and v > 0):
                    results[k] = v

        return results

    def parse_html_summary(self, htm_path: str | Path) -> dict[str, float]:
        """Extract annual energy metrics directly from eplusout.htm tabular summary reports."""
        path = Path(htm_path)
        if not path.is_file():
            return {}

        extracted: dict[str, float] = {}
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")

            # Match Electricity Total End Uses (GJ or kWh)
            elec_match = re.search(r"Total End Uses.*?Electricity.*?>\s*([\d\.,]+)\s*<", content, re.IGNORECASE | re.DOTALL)
            if elec_match:
                val = float(elec_match.group(1).replace(",", ""))
                extracted["electricity"] = round(val * 277.778 if val < 1000 and "GJ" in content else val, 2)

            # Match Cooling End Uses
            cool_match = re.search(r"Cooling.*?Electricity.*?>\s*([\d\.,]+)\s*<", content, re.IGNORECASE | re.DOTALL)
            if cool_match:
                val = float(cool_match.group(1).replace(",", ""))
                extracted["cooling"] = round(val * 277.778 if val < 1000 and "GJ" in content else val, 2)

            # Match Heating End Uses
            heat_match = re.search(r"Heating.*?Electricity.*?>\s*([\d\.,]+)\s*<", content, re.IGNORECASE | re.DOTALL)
            if heat_match:
                val = float(heat_match.group(1).replace(",", ""))
                extracted["heating"] = round(val * 277.778 if val < 1000 and "GJ" in content else val, 2)
        except Exception:
            pass

        return extracted

    @staticmethod
    def _match_columns(headers: list[str], pattern_dict: dict[str, tuple[str, ...]]) -> dict[str, list[str]]:
        """Map output headers to requested pattern tuples."""
        matched: dict[str, list[str]] = {}
        for metric, patterns in pattern_dict.items():
            matched[metric] = [
                header for header in headers
                if any(pattern in header.lower() for pattern in patterns)
            ]
        return matched

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        """Convert a CSV string value to float safely."""
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _to_kwh(value: float, header: str) -> float:
        """Convert joule-based EnergyPlus values [J] to kWh; preserve kWh values."""
        header_lower = header.lower()
        if "[j]" in header_lower:
            return value / 3_600_000.0
        elif "[kj]" in header_lower:
            return value / 3_600.0
        elif "[mj]" in header_lower:
            return value / 3.6
        elif "[gj]" in header_lower:
            return value * 277.778
        return value

