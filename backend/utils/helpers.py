"""Small reusable filesystem and timestamp helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


def create_directory(path: str | Path) -> Path:
    """Create a directory and its parents when absent."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_file(path: str | Path, suffixes: tuple[str, ...] | None = None) -> Path:
    """Validate that a regular file exists and has an allowed suffix."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    if suffixes and file_path.suffix.lower() not in suffixes:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    return file_path


def current_timestamp() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def generate_uuid() -> str:
    """Return a random UUID string."""
    return str(uuid4())
