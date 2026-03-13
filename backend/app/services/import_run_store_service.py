from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.models.pst_import_models import ImportRun, ImportedEmail

logger = logging.getLogger(__name__)

_PERSIST_DIR = Path(__file__).resolve().parents[3] / "data" / "import_runs"


class _ImportRunStore:
    def __init__(self, persist_dir: Path | None = None) -> None:
        self._persist_dir = persist_dir or _PERSIST_DIR
        self._runs: dict[str, ImportRun] = {}
        self._lock = Lock()
        self._load()

    def _meta_path(self, import_run_id: str) -> Path:
        return self._persist_dir / f"{import_run_id}.json"

    def _emails_path(self, import_run_id: str) -> Path:
        return self._persist_dir / f"{import_run_id}.emails.json"

    def _write_json_atomic(self, path: Path, payload: dict | list) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_path.replace(path)

    def _quarantine_file(self, path: Path) -> None:
        if not path.exists():
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        corrupt_path = path.with_suffix(f"{path.suffix}.corrupt-{timestamp}")
        try:
            path.replace(corrupt_path)
            logger.warning("Korruptionsverdächtige Datei verschoben: %s -> %s", path, corrupt_path)
        except OSError:
            logger.exception("Korruptionsverdächtige Datei konnte nicht verschoben werden: %s", path)

    def _load_emails(self, import_run_id: str) -> list[ImportedEmail]:
        emails_path = self._emails_path(import_run_id)
        if not emails_path.exists():
            return []

        try:
            raw_emails = json.loads(emails_path.read_text(encoding="utf-8"))
            if not isinstance(raw_emails, list):
                raise ValueError("E-Mail-Datei enthält keine Liste.")
            return [ImportedEmail(**email) for email in raw_emails]
        except Exception as exc:  # noqa: BLE001
            logger.exception("ImportRun-E-Mails konnten nicht geladen werden: %s", import_run_id)
            self._quarantine_file(emails_path)
            return []

    def _load(self) -> None:
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        for meta_path in self._persist_dir.glob("*.json"):
            if meta_path.name.endswith(".emails.json"):
                continue

            try:
                raw_meta = json.loads(meta_path.read_text(encoding="utf-8"))
                if not isinstance(raw_meta, dict):
                    raise ValueError("ImportRun-Metadaten enthalten kein JSON-Objekt.")
                import_run_id = str(raw_meta["import_run_id"])
                emails = self._load_emails(import_run_id)
                run = ImportRun(**raw_meta, imported_emails=emails)
                self._runs[import_run_id] = run
            except Exception as exc:  # noqa: BLE001
                logger.exception("ImportRun-Metadaten konnten nicht geladen werden: %s", meta_path)
                self._quarantine_file(meta_path)

    def _persist_run(self, run: ImportRun) -> ImportRun:
        meta_payload = run.model_dump(mode="json", exclude={"imported_emails"})
        emails_payload = [email.model_dump(mode="json") for email in run.imported_emails]
        self._write_json_atomic(self._meta_path(run.import_run_id), meta_payload)
        self._write_json_atomic(self._emails_path(run.import_run_id), emails_payload)
        self._runs[run.import_run_id] = run
        return run

    def save(self, run: ImportRun, emails: list[ImportedEmail] | None = None) -> ImportRun:
        with self._lock:
            stored = run.model_copy(
                update={"imported_emails": emails if emails is not None else list(run.imported_emails)}
            )
            return self._persist_run(stored)

    def get(self, import_run_id: str) -> ImportRun | None:
        with self._lock:
            run = self._runs.get(import_run_id)
            return None if run is None else run.model_copy(deep=True)

    def update(self, run: ImportRun) -> ImportRun:
        with self._lock:
            existing = self._runs.get(run.import_run_id)
            imported_emails = list(run.imported_emails)
            if not imported_emails and existing is not None:
                imported_emails = list(existing.imported_emails)
            stored = run.model_copy(update={"imported_emails": imported_emails})
            return self._persist_run(stored)

    def list_runs(self) -> list[ImportRun]:
        with self._lock:
            return [run.model_copy(deep=True) for run in self._runs.values()]


_store = _ImportRunStore()


def save_run(run: ImportRun, emails: list[ImportedEmail] | None = None) -> ImportRun:
    return _store.save(run, emails)


def get_run(import_run_id: str) -> ImportRun | None:
    return _store.get(import_run_id)


def update_run(run: ImportRun) -> ImportRun:
    return _store.update(run)


def list_runs() -> list[ImportRun]:
    return _store.list_runs()
