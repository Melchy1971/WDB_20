from app.models.settings_models import AiProvider


class SettingsService:
    """In-Memory-Speicher für Anwendungseinstellungen."""

    def __init__(self) -> None:
        self._active_provider: AiProvider = "none"

    def get_active_provider(self) -> AiProvider:
        return self._active_provider

    def set_active_provider(self, provider: AiProvider) -> None:
        self._active_provider = provider


_instance = SettingsService()


def get_settings_service() -> SettingsService:
    return _instance
