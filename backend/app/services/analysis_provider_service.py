from __future__ import annotations

from typing import Protocol

from app.adapters.dnabot_adapter import DnaBotAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.models.analysis_models import AnalysisResult
from app.models.pst_import_models import ImportedEmail
from app.services.settings_service import get_settings_service


class AnalysisProvider(Protocol):
    def analyze_import_run(
        self,
        import_run_id: str,
        emails: list[ImportedEmail],
    ) -> list[AnalysisResult]:
        ...


class AnalysisProviderService:
    """Zentrale Provider-Abstraktion für die Analysepipeline."""

    def __init__(self) -> None:
        self._settings = get_settings_service()
        self._providers: dict[str, AnalysisProvider] = {
            "ollama": OllamaAdapter(),
            "dnabot": DnaBotAdapter(),
        }

    def analyze_import_run(
        self,
        import_run_id: str,
        emails: list[ImportedEmail],
    ) -> list[AnalysisResult]:
        provider = self._settings.require_active_provider()
        adapter = self._providers.get(provider)
        if adapter is None:
            raise RuntimeError(f"Unbekannter KI-Provider: {provider}")
        return adapter.analyze_import_run(import_run_id=import_run_id, emails=emails)


_provider_service = AnalysisProviderService()


def get_analysis_provider_service() -> AnalysisProviderService:
    return _provider_service
