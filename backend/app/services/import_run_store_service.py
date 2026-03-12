"""In-Memory-Store für ImportRun-Datensätze."""

from app.models.pst_import_models import ImportRun
from app.models.pst_import_models import ImportedEmail


class _ImportRunStore:
    def __init__(self) -> None:
        self._runs: dict[str, ImportRun] = {}

    def save(self, run: ImportRun, emails: list[ImportedEmail] | None = None) -> ImportRun:
        if emails is not None:
            run.imported_emails = emails
        self._runs[run.import_run_id] = run
        return run

    def get(self, import_run_id: str) -> ImportRun | None:
        return self._runs.get(import_run_id)

    def update(self, run: ImportRun) -> ImportRun:
        self._runs[run.import_run_id] = run
        return run


_store = _ImportRunStore()


def save_run(run: ImportRun, emails: list[ImportedEmail] | None = None) -> ImportRun:
    return _store.save(run, emails)


def get_run(import_run_id: str) -> ImportRun | None:
    return _store.get(import_run_id)


def update_run(run: ImportRun) -> ImportRun:
    return _store.update(run)
