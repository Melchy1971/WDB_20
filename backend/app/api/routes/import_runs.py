from fastapi import APIRouter, HTTPException

from app.models.analysis_models import ImportRunAnalysisResponse, StartImportRunAnalysisResponse
from app.models.pst_import_models import ImportRunResponse
from app.services import import_job_service
from app.services.analysis_service import get_analysis_service
from app.services.settings_service import NoActiveAiProviderError

router = APIRouter(prefix="/import-runs", tags=["import-runs"])


@router.get(
    "/{import_run_id}",
    response_model=ImportRunResponse,
    summary="Import-Run abrufen",
    description="Gibt Metriken, Status und importierte E-Mails eines PST-Importlaufs zurück.",
)
def get_import_run(import_run_id: str) -> ImportRunResponse:
    run = import_job_service.get_run(import_run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"ImportRun nicht gefunden: {import_run_id}")

    return ImportRunResponse(
        import_run_id=run.import_run_id,
        source_id=run.source_id,
        selected_node_ids=run.selected_node_ids,
        email_count=run.email_count,
        imported_count=run.imported_count,
        duplicate_count=run.duplicate_count,
        attachment_count=run.attachment_count,
        total_folder_count=run.total_folder_count,
        processed_folder_count=run.processed_folder_count,
        total_message_count_estimate=run.total_message_count_estimate,
        processed_message_count=run.processed_message_count,
        progress_percent=run.progress_percent,
        processed_batches=run.processed_batches,
        failed_batches=run.failed_batches,
        batch_size=run.batch_size,
        error_message=run.error_message,
        status=run.status,
        imported_emails=run.imported_emails,
    )


@router.post(
    "/{import_run_id}/analysis",
    response_model=StartImportRunAnalysisResponse,
    summary="Analyse starten",
    description="Startet die KI-Analyse für einen ImportRun über den aktiven Provider.",
)
def start_import_run_analysis(import_run_id: str) -> StartImportRunAnalysisResponse:
    analysis_service = get_analysis_service()
    try:
        return analysis_service.start_import_run_analysis(import_run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NoActiveAiProviderError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Analyse fehlgeschlagen: {exc}") from exc


@router.get(
    "/{import_run_id}/analysis",
    response_model=ImportRunAnalysisResponse,
    summary="Analyseergebnisse abrufen",
    description="Lädt die gespeicherten Analyseergebnisse eines ImportRuns.",
)
def get_import_run_analysis(import_run_id: str) -> ImportRunAnalysisResponse:
    analysis_service = get_analysis_service()
    try:
        return analysis_service.get_import_run_analysis(import_run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
