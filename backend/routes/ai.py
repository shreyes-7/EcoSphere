"""Routes exposing the local Ollama integration."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models.request_models import ChatRequest
from backend.services.ollama_service import OllamaService, get_ollama_service
from backend.utils.exceptions import OllamaError

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/health")
async def ai_health(service: OllamaService = Depends(get_ollama_service)) -> dict[str, str]:
    """Report whether the Ollama server is reachable."""
    return {"status": "healthy" if await service.health_check() else "unavailable"}


@router.get("/models")
async def ai_models(service: OllamaService = Depends(get_ollama_service)) -> dict[str, list[dict[str, Any]]]:
    """List models currently available in Ollama."""
    try:
        return {"models": await service.list_models()}
    except OllamaError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.post("/chat")
async def ai_chat(
    request: ChatRequest, service: OllamaService = Depends(get_ollama_service)
) -> dict[str, Any]:
    """Forward a prompt to the configured Ollama model."""
    try:
        return await service.generate(request.prompt)
    except OllamaError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
