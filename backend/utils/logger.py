"""Centralized logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from backend.config import Settings
from backend.utils.helpers import create_directory


def configure_logging(settings: Settings) -> None:
    """Configure console and rotating file logging once per process."""
    root_logger = logging.getLogger()
    if getattr(root_logger, "_ecosphere_configured", False):
        return

    create_directory(settings.log_file.parent)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        settings.log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger._ecosphere_configured = True  # type: ignore[attr-defined]


def get_logger(name: str) -> logging.Logger:
    """Return a named application logger."""
    return logging.getLogger(name)
