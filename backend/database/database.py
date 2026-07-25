"""SQLAlchemy database setup and FastAPI dependency."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import get_settings
from backend.utils.helpers import create_directory

settings = get_settings()
engine_options: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
    sqlite_path = settings.database_url.removeprefix("sqlite:///")
    if sqlite_path and sqlite_path != ":memory:":
        create_directory(Path(sqlite_path).parent)

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def initialize_database() -> None:
    """Create tables and add Phase 2 simulation columns to SQLite databases."""
    Base.metadata.create_all(bind=engine)
    if not settings.database_url.startswith("sqlite"):
        return

    existing_columns = {column["name"] for column in inspect(engine).get_columns("simulations")}
    required_columns = {
        "output_folder": "VARCHAR(1024)",
        "total_energy": "FLOAT",
        "electricity": "FLOAT",
        "cooling": "FLOAT",
        "heating": "FLOAT",
        "hvac": "FLOAT",
    }
    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE simulations ADD COLUMN {column_name} {column_type}"))


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request."""
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()
