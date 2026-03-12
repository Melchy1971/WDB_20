from fastapi import APIRouter, HTTPException

from app.models.job_models import (
    ImportJobStatusResponse,
    StartImportJobRequest,
    StartImportJobResponse,
)
from app.services import import_job_service, source_registry_service, source_selection_service

# ── Router: POST /sources/{source_id}/import-jobs ─────────────────────────────
sources_import_router = APIRouter(prefix="/sources", tags=["import-jobs"])


@sources_import_router.post(
    "/{source_id}/import-jobs",
    response_model=StartImportJobResponse,
    status_code=202,
    summary="Import-Job starten",
    description=(
        "Startet einen neuen PST-Import-Job für die angegebene Quelle. "
        "Der Job ist aktuell ein Stub – kein echter Import wird ausgeführt."
    ),
)
def start_import_job(
    source_id: str,
    body: StartImportJobRequest,  # noqa: ARG001 – reserviert für zukünftige Optionen
) -> StartImportJobResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    if source.source_type != "PST":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Import-Jobs sind nur für PST-Quellen verfügbar "
                f"(Quellentyp dieser Quelle: {source.source_type})."
            ),
        )

    selected_node_ids = source_selection_service.get_selection(source_id)
    if len(selected_node_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="Keine Knoten ausgewählt. Wählen Sie zuerst Knoten in der PST-Struktur.",
        )

    job = import_job_service.start_import_job(
        source_id=source_id,
        selected_count=len(selected_node_ids),
    )
    return StartImportJobResponse(
        job_id=job.job_id,
        source_id=job.source_id,
        job_type=job.job_type,
        status=job.status,
        selected_count=job.selected_count,
        message=job.message,
    )


# ── Router: GET /import-jobs/{job_id} ─────────────────────────────────────────
import_jobs_router = APIRouter(prefix="/import-jobs", tags=["import-jobs"])


@import_jobs_router.get(
    "/{job_id}",
    response_model=ImportJobStatusResponse,
    summary="Job-Status abfragen",
    description="Gibt den aktuellen Status eines Import-Jobs zurück.",
)
def get_import_job_status(job_id: str) -> ImportJobStatusResponse:
    job = import_job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job nicht gefunden: {job_id}")
    return ImportJobStatusResponse(
        job_id=job.job_id,
        source_id=job.source_id,
        job_type=job.job_type,
        status=job.status,
        selected_count=job.selected_count,
        message=job.message,
    )
