from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["queued", "running", "finished", "failed"]
JobType = Literal["PST_IMPORT"]


class ImportJob(BaseModel):
    """Internes Job-Modell – wird im In-Memory-Store gehalten.

    Enthält dieselben Felder wie die API-Response-Modelle.  Das interne
    Modell bleibt bewusst getrennt, damit es in Zukunft interne Felder
    aufnehmen kann (z. B. Timestamps, Node-IDs-Snapshot), ohne die
    öffentliche API zu beeinflussen.
    """

    job_id: str
    source_id: str
    job_type: JobType
    status: JobStatus
    selected_count: int
    message: str


class StartImportJobRequest(BaseModel):
    """Request-Body für POST /sources/{source_id}/import-jobs.

    Aktuell leer – alle benötigten Daten liest der Server selbst aus dem
    Selection-Store.  Reserviert für zukünftige Optionen (z. B. dry_run).
    """


class StartImportJobResponse(BaseModel):
    """Antwort auf POST /sources/{source_id}/import-jobs.

    Absichtlich als eigener Typ definiert – kann in Zukunft Felder
    enthalten, die nur beim Start relevant sind (z. B. queue_position).
    """

    job_id: str
    source_id: str
    job_type: JobType
    status: JobStatus
    selected_count: int
    message: str


class ImportJobStatusResponse(BaseModel):
    """Antwort auf GET /import-jobs/{job_id}.

    Absichtlich als eigener Typ definiert – kann in Zukunft Felder
    enthalten, die nur beim Polling relevant sind (z. B. progress_percent).
    """

    job_id: str
    source_id: str
    job_type: JobType
    status: JobStatus
    selected_count: int
    message: str
