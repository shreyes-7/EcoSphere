"""Client service for the local Ollama HTTP API."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import Depends

from backend.config import Settings, get_settings
from backend.utils.exceptions import OllamaError


class OllamaService:
    """Communicate with a locally running Ollama server."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model
        self._timeout = settings.ollama_timeout_seconds

    async def generate(self, prompt: str) -> dict[str, Any]:
        """Generate a complete non-streaming response for a prompt."""
        payload = {"model": self._model, "prompt": prompt, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(f"{self._base_url}/api/generate", json=payload)
        except httpx.TimeoutException as error:
            raise OllamaError("Ollama request timed out") from error
        except httpx.RequestError as error:
            raise OllamaError("Ollama server is unavailable") from error

        if response.status_code == 404:
            raise OllamaError(f"Configured Ollama model is unavailable: {self._model}")
        if response.is_error:
            raise OllamaError(f"Ollama request failed: {response.text}")
        try:
            return response.json()
        except ValueError as error:
            raise OllamaError("Ollama returned an invalid JSON response") from error

    async def health_check(self) -> bool:
        """Return whether Ollama responds to its model-list endpoint."""
        try:
            async with httpx.AsyncClient(timeout=min(self._timeout, 5.0)) as client:
                response = await client.get(f"{self._base_url}/api/tags")
            return response.is_success
        except httpx.RequestError:
            return False

    async def list_models(self) -> list[dict[str, Any]]:
        """Return models installed in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}/api/tags")
        except httpx.TimeoutException as error:
            raise OllamaError("Ollama model listing timed out") from error
        except httpx.RequestError as error:
            raise OllamaError("Ollama server is unavailable") from error
        if response.is_error:
            raise OllamaError(f"Ollama model listing failed: {response.text}")
        try:
            payload = response.json()
            return payload.get("models", [])
        except ValueError as error:
            raise OllamaError("Ollama returned an invalid JSON response") from error


def get_ollama_service(
    settings: Settings = Depends(get_settings),
) -> OllamaService:
    """Create an Ollama service for dependency injection."""
    return OllamaService(settings)
