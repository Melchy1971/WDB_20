"""In-Memory-Verwaltung von PST-Import-Jobs inklusive ImportRun-Lebenszyklus."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.job_models import ImportJob
from app.models.pst_import_models import ImportRun
from app.models.tree_models import SourceTreeResponse
from app.services import import_run_store_service
from app.services import pst_import_service
from app.services.pst_import_neo4j_ingest_service import PstImportNeo4jIngestService

_jobs: dict[str, ImportJob] = {}

_mail_extractor = pst_import_service.LibratomPstMailExtractor()
_neo4j_ingest_service = PstImportNeo4jIngestService()


def start_import_job(
    source_id: str,
    source_path: str,
    selected_node_ids: list[str],
    tree: SourceTreeResponse,
) -> ImportJob:
    run = pst_import_service.build_import_run(
        source_id=source_id,
        source_path=source_path,
        selected_node_ids=selected_node_ids,
        tree=tree,
    )
    import_run_store_service.save_run(run)

    job_id = str(uuid4())
    job = ImportJob(
        job_id=job_id,
        source_id=source_id,
        job_type="PST_IMPORT",
        status="queued",
        import_run_id=run.import_run_id,
        selected_count=len(run.selected_node_ids),
        message=f"Import vorbereitet: {len(run.selected_node_ids)} Ordner ausgewählt.",
    )
    _jobs[job_id] = job

    _process_job(job_id)
    return _jobs[job_id]


def _process_job(job_id: str) -> None:
    job = _jobs[job_id]
    if job.import_run_id is None:
        job.status = "failed"
        job.message = "ImportRun fehlt."
        job.error_message = "ImportRun fehlt."
        return

    run = import_run_store_service.get_run(job.import_run_id)
    if run is None:
        job.status = "failed"
        job.message = f"ImportRun nicht gefunden: {job.import_run_id}"
        job.error_message = job.message
        return

    job.status = "running"
    job.message = "PST-Import läuft."
    run.status = "running"
    run.error_message = None
    import_run_store_service.update_run(run)

    try:
        emails = _mail_extractor.extract_from_run(run)
        run.email_count = len(emails)
        run.attachment_count = pst_import_service.count_attachments(emails)
        import_run_store_service.save_run(run, emails)

        try:
            _neo4j_ingest_service.ingest_run(run, emails)
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.finished_at = datetime.now(timezone.utc)
            run.error_message = f"Neo4j-Ingest fehlgeschlagen: {exc}"
            import_run_store_service.update_run(run)

            job.status = "failed"
            job.error_message = run.error_message
            job.message = "PST-Import fehlgeschlagen: Neo4j-Ingest nicht erfolgreich."
            return

        run.status = "finished"
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = None
        import_run_store_service.update_run(run)

        job.status = "finished"
        job.error_message = None
        job.message = "PST-Import und Neo4j-Rohpersistenz abgeschlossen."
    except Exception as exc:  # noqa: BLE001
        run.status = "failed"
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = str(exc)
        import_run_store_service.update_run(run)

        job.status = "failed"
        job.error_message = str(exc)
        job.message = f"PST-Import fehlgeschlagen: {exc}"


def get_job(job_id: str) -> ImportJob | None:
    return _jobs.get(job_id)


def get_run(import_run_id: str) -> ImportRun | None:
    return import_run_store_service.get_run(import_run_id)
