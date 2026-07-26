"""Application configuration and dependency providers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)


class Settings:
    """Typed application settings loaded from the environment."""

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "EcoSphere")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", "8000"))
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
        self.ollama_timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
        self.energyplus_path = os.getenv("ENERGYPLUS_PATH", "")
        self.weather_file = os.getenv("WEATHER_FILE", "")
        self.building_idf = os.getenv("BUILDING_IDF", "")
        self.output_directory = Path(os.getenv("OUTPUT_DIRECTORY", str(BASE_DIR / "simulation_output")))
        self.upload_directory = Path(os.getenv("UPLOAD_DIRECTORY", str(BASE_DIR / "uploads")))
        self.simulation_timeout_seconds = float(os.getenv("SIMULATION_TIMEOUT_SECONDS", "600"))
        self.target_temperature_min = float(os.getenv("TARGET_TEMPERATURE_MIN", "22"))
        self.target_temperature_max = float(os.getenv("TARGET_TEMPERATURE_MAX", "25"))
        self.target_humidity_min = float(os.getenv("TARGET_HUMIDITY_MIN", "40"))
        self.target_humidity_max = float(os.getenv("TARGET_HUMIDITY_MAX", "60"))
        self.target_pmv_min = float(os.getenv("TARGET_PMV_MIN", "-0.5"))
        self.target_pmv_max = float(os.getenv("TARGET_PMV_MAX", "0.5"))
        self.high_hvac_energy_threshold = float(os.getenv("HIGH_HVAC_ENERGY_THRESHOLD", "100"))
        self.high_carbon_intensity_threshold = float(
            os.getenv("HIGH_CARBON_INTENSITY_THRESHOLD", "0.4")
        )
        self.energy_price_per_kwh = float(os.getenv("ENERGY_PRICE_PER_KWH", "0.12"))
        self.carbon_kg_per_kwh = float(os.getenv("CARBON_KG_PER_KWH", "0.4"))
        self.max_expected_savings_percent = float(
            os.getenv("MAX_EXPECTED_SAVINGS_PERCENT", "25")
        )
        database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ecosphere.db'}")
        sqlite_prefix = "sqlite:///"
        if database_url.startswith(sqlite_prefix):
            database_path = database_url.removeprefix(sqlite_prefix)
            if database_path and not Path(database_path).is_absolute():
                resolved_path = (BASE_DIR / database_path).resolve()
                database_url = f"{sqlite_prefix}{resolved_path.as_posix()}"
        self.database_url = database_url
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = Path(os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "ecosphere.log")))


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()


settings = get_settings()
