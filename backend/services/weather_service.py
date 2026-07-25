"""Weather-file parsing and validation service for EnergyPlus EPW files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.utils.exceptions import WeatherFileMissing


@dataclass(frozen=True)
class EPWLocation:
    """Location metadata extracted from an EPW header."""

    city: str
    state_province: str
    country: str
    data_source: str
    wmo_number: str
    latitude: float
    longitude: float
    time_zone: float
    elevation: float


@dataclass(frozen=True)
class EPWWeatherSummary:
    """Aggregated climate metrics parsed directly from EPW weather records."""

    location: EPWLocation
    avg_dry_bulb_temp: float
    max_dry_bulb_temp: float
    min_dry_bulb_temp: float
    avg_relative_humidity: float
    avg_direct_solar: float
    avg_wind_speed: float
    total_hours: int


class WeatherService:
    """Validate and parse local EnergyPlus weather (EPW) files."""

    def weather_exists(self, weather_file: str | Path) -> bool:
        """Return whether a local weather file exists."""
        return Path(weather_file).is_file()

    def validate_weather_file(self, weather_file: str | Path) -> Path:
        """Return a validated EPW path or raise a domain exception."""
        path = Path(weather_file)
        if not self.weather_exists(path) or path.suffix.lower() != ".epw":
            raise WeatherFileMissing(f"Weather file missing or invalid: {path}")
        if path.stat().st_size == 0:
            raise WeatherFileMissing(f"Weather file is empty: {path}")
        return path

    def parse_epw_weather(self, weather_file: str | Path) -> EPWWeatherSummary:
        """Parse an EPW file and extract location metadata and real hourly weather averages."""
        path = self.validate_weather_file(weather_file)

        try:
            with path.open("r", encoding="utf-8-sig", errors="ignore") as file:
                lines = [file.readline() for _ in range(8)]
                if not lines or not lines[0].upper().startswith("LOCATION"):
                    raise WeatherFileMissing(f"Invalid or corrupted EPW header in file: {path}")

                # Parse LOCATION line
                # LOCATION,City,State,Country,Source,WMO,Lat,Long,TZ,Elev
                loc_parts = [p.strip() for p in lines[0].split(",")]
                location = EPWLocation(
                    city=loc_parts[1] if len(loc_parts) > 1 else "Unknown",
                    state_province=loc_parts[2] if len(loc_parts) > 2 else "Unknown",
                    country=loc_parts[3] if len(loc_parts) > 3 else "Unknown",
                    data_source=loc_parts[4] if len(loc_parts) > 4 else "TMY3",
                    wmo_number=loc_parts[5] if len(loc_parts) > 5 else "000000",
                    latitude=float(loc_parts[6]) if len(loc_parts) > 6 else 0.0,
                    longitude=float(loc_parts[7]) if len(loc_parts) > 7 else 0.0,
                    time_zone=float(loc_parts[8]) if len(loc_parts) > 8 else 0.0,
                    elevation=float(loc_parts[9]) if len(loc_parts) > 9 else 0.0,
                )

                # Parse data rows (starts from line 9)
                reader = csv.reader(file)
                dry_bulbs: list[float] = []
                humidities: list[float] = []
                direct_solars: list[float] = []
                wind_speeds: list[float] = []

                for row in reader:
                    if len(row) >= 22:
                        try:
                            # EPW columns (0-indexed):
                            # Col 6: Dry Bulb Temp [C]
                            # Col 8: Relative Humidity [%]
                            # Col 14: Direct Normal Radiation [Wh/m2]
                            # Col 21: Wind Speed [m/s]
                            db = float(row[6])
                            rh = float(row[8])
                            sol = float(row[14])
                            ws = float(row[21])

                            if -90.0 <= db <= 70.0:
                                dry_bulbs.append(db)
                            if 0.0 <= rh <= 100.0:
                                humidities.append(rh)
                            if sol >= 0.0:
                                direct_solars.append(sol)
                            if ws >= 0.0:
                                wind_speeds.append(ws)
                        except (ValueError, IndexError):
                            continue

                if not dry_bulbs:
                    raise WeatherFileMissing(f"No valid hourly weather data found in EPW file: {path}")

                return EPWWeatherSummary(
                    location=location,
                    avg_dry_bulb_temp=round(sum(dry_bulbs) / len(dry_bulbs), 2),
                    max_dry_bulb_temp=round(max(dry_bulbs), 2),
                    min_dry_bulb_temp=round(min(dry_bulbs), 2),
                    avg_relative_humidity=round(sum(humidities) / len(humidities), 2) if humidities else 50.0,
                    avg_direct_solar=round(sum(direct_solars) / len(direct_solars), 2) if direct_solars else 0.0,
                    avg_wind_speed=round(sum(wind_speeds) / len(wind_speeds), 2) if wind_speeds else 0.0,
                    total_hours=len(dry_bulbs),
                )
        except Exception as error:
            raise WeatherFileMissing(f"Error parsing EPW weather file {path}: {error}") from error

