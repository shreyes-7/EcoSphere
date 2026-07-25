"""Weather-file validation service."""

from __future__ import annotations

from pathlib import Path

from backend.utils.exceptions import WeatherFileMissing


class WeatherService:
    """Validate local EnergyPlus weather inputs."""

    def weather_exists(self, weather_file: str | Path) -> bool:
        """Return whether a local weather file exists."""
        return Path(weather_file).is_file()

    def validate_weather_file(self, weather_file: str | Path) -> Path:
        """Return a validated EPW path or raise a domain exception."""
        path = Path(weather_file)
        if not self.weather_exists(path) or path.suffix.lower() != ".epw":
            raise WeatherFileMissing(f"Weather file missing or invalid: {path}")
        return path

    def fetch_weather_api(self, *_: object, **__: object) -> None:
        """TODO: Integrate an external weather API in a future phase."""
        return None
