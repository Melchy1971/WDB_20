from __future__ import annotations

from app.models.analysis_models import (
    ImportRunAnalysisRecord,
    ImportRunAnalysisResponse,
    StartImportRunAnalysisResponse,
)
from app.services import import_job_service
from app.services.analysis_provider_service import get_analysis_provider_service

_records: dict[str, ImportRunAnalysisRecord] = {}


class AnalysisService:
    def __init__(self) -> None:
        self._provider_service = get_analysis_provider_service()

    def start_import_run_analysis(self, import_run_id: str) -> StartImportRunAnalysisResponse:
        run = import_job_service.get_run(import_run_id)
        if run is None:
            raise KeyError(f"ImportRun nicht gefunden: {import_run_id}")

        record = ImportRunAnalysisRecord(
            import_run_id=import_run_id,
            status="running",
            results=[],
            error_message=None,
        )
        _records[import_run_id] = record

        try:
            results = self._provider_service.analyze_import_run(
                import_run_id=import_run_id,
                emails=run.imported_emails,
            )
            record.status = "finished"
            record.results = results
            record.error_message = None
            message = "Analyse abgeschlossen."
        except Exception as exc:  # noqa: BLE001
            record.status = "failed"
            record.results = []
            record.error_message = str(exc)
            raise
        finally:
            _records[import_run_id] = record

        return StartImportRunAnalysisResponse(
            import_run_id=import_run_id,
            status=record.status,
            message=message,
        )

    def get_import_run_analysis(self, import_run_id: str) -> ImportRunAnalysisResponse:
        record = _records.get(import_run_id)
        if record is None:
            raise KeyError(f"Analyse nicht gefunden: {import_run_id}")

        return ImportRunAnalysisResponse(
            import_run_id=record.import_run_id,
            status=record.status,
            results=record.results,
        )


_service = AnalysisService()


def get_analysis_service() -> AnalysisService:
    return _service
