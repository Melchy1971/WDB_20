from app.models.settings_models import AiProvider


class NoActiveAiProviderError(RuntimeError):
    pass


class SettingsService:
    """In-Memory-Speicher für Anwendungseinstellungen."""

    def __init__(self) -> None:
        self._active_provider: AiProvider = "none"

    def get_active_provider(self) -> AiProvider:
        return self._active_provider

    def set_active_provider(self, provider: AiProvider) -> None:
        self._active_provider = provider

    def require_active_provider(self) -> AiProvider:
        provider = self._active_provider
        if provider == "none":
            raise NoActiveAiProviderError(
                "Kein aktiver KI-Provider konfiguriert. "
                "Setzen Sie /settings/ai-provider auf 'ollama' oder 'dnabot'."
            )
        return provider


_instance = SettingsService()


def get_settings_service() -> SettingsService:
    return _instance
