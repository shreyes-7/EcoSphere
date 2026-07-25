"""Compatibility ASGI entrypoint for Uvicorn."""

try:
    from backend.main import app
except ModuleNotFoundError:
    from main import app

__all__ = ["app"]
