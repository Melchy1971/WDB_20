"""
import_job_service.py

In-Memory-Verwaltung von Import-Jobs.
Der eigentliche PST-Import ist noch nicht implementiert – Jobs werden
sofort als „finished" (Stub) abgelegt.
"""

import uuid

from app.models.job_models import ImportJob

# ── In-Memory-Speicher ────────────────────────────────────────────────────────
_jobs: dict[str, ImportJob] = {}


def start_import_job(source_id: str, selected_count: int) -> ImportJob:
    """Legt einen neuen PST_IMPORT-Job an und gibt ihn zurück.

    Aktuell Stub: Status wird sofort auf „finished" gesetzt.
    Sobald ein echter Import implementiert ist, kann hier ein
    Background-Task gestartet werden (z. B. via asyncio / FastAPI BackgroundTasks).
    """
    job_id = str(uuid.uuid4())
    job = ImportJob(
        job_id=job_id,
        source_id=source_id,
        job_type="PST_IMPORT",
        status="finished",
        selected_count=selected_count,
        message=(
            f"Stub: {selected_count} Element(e) vorgemerkt. "
            "Echter PST-Import noch nicht implementiert."
        ),
    )
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> ImportJob | None:
    """Gibt den Job mit der angegebenen ID zurück oder None."""
    return _jobs.get(job_id)
