from fastapi import APIRouter, HTTPException

from app.models.job_models import (
    ImportJobStatusResponse,
    StartImportJobRequest,
    StartImportJobResponse,
)
from app.services import import_job_service, source_registry_service, source_selection_service
from app.services.pst_parser_service import PstParserService


def _build_job_response_payload(job):
    return {
        "job_id": job.job_id,
        "source_id": job.source_id,
        "job_type": job.job_type,
        "status": job.status,
        "import_run_id": job.import_run_id,
        "selected_count": job.selected_count,
        "error_message": job.error_message,
        "message": job.message,
    }


def _build_pst_tree_or_raise(source_id: str, pst_path: str):
    try:
        return PstParserService.build_tree(
            source_id=source_id,
            pst_path=pst_path,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"PST-Parser nicht verfügbar: {exc}",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"PST-Datei konnte nicht gelesen werden: {exc}",
        ) from exc

# ── Router: POST /sources/{source_id}/import-jobs ─────────────────────────────
sources_import_router = APIRouter(prefix="/sources", tags=["import-jobs"])


@sources_import_router.post(
    "/{source_id}/import-jobs",
    response_model=StartImportJobResponse,
    status_code=202,
    summary="Import-Job starten",
    description=(
        "Startet einen neuen PST-Import-Job für die angegebene Quelle. "
        "Der Job extrahiert Roh-E-Mails aus den selektierten PST-Ordnern."
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

    tree = _build_pst_tree_or_raise(source_id=source_id, pst_path=source.source_path)
    valid_node_ids = PstParserService.collect_valid_node_ids(tree)
    selected_node_ids = source_selection_service.sanitize_selection(source_id, valid_node_ids)

    if len(selected_node_ids) == 0:
        raise HTTPException(
            status_code=400,

        )

    job = import_job_service.start_import_job(
        source_id=source_id,
        source_path=source.source_path,
        selected_node_ids=selected_node_ids,
        tree=tree,
    )
    return StartImportJobResponse(**_build_job_response_payload(job))


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
    return ImportJobStatusResponse(**_build_job_response_payload(job))
