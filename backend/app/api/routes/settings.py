from fastapi import APIRouter

from app.models.settings_models import AiProviderResponse, SetAiProviderRequest, SetAiProviderResponse
from app.services.settings_service import get_settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/ai-provider", response_model=AiProviderResponse)
def get_ai_provider() -> AiProviderResponse:
    service = get_settings_service()
    return AiProviderResponse(active_provider=service.get_active_provider())


@router.post("/ai-provider", response_model=SetAiProviderResponse)
def set_ai_provider(request: SetAiProviderRequest) -> SetAiProviderResponse:
    service = get_settings_service()
    service.set_active_provider(request.active_provider)
    # Lese den vom Service gespeicherten Wert zurück — kein Echoing des Requests.
    return SetAiProviderResponse(status="updated", active_provider=service.get_active_provider())
