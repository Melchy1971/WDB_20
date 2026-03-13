import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.pst_import_models import ImportRun, ImportedAttachment, ImportedEmail
from app.services.import_run_store_service import _ImportRunStore

_TEST_ROOT = Path(__file__).resolve().parents[2] / "data" / ".test_import_runs"


def _test_dir() -> Path:
    path = _TEST_ROOT / str(uuid4())
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cleanup(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _build_run(import_run_id: str = "run-1") -> ImportRun:
    return ImportRun(
        import_run_id=import_run_id,
        source_id="source-1",
        source_path=r"C:\mail\archive.pst",
        selected_node_ids=["node-1", "node-2"],
        selected_folder_paths=["Mailbox", "Mailbox/Inbox"],
        status="running",
        started_at=datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc),
        finished_at=None,
        email_count=0,
        attachment_count=0,
        error_message=None,
        imported_emails=[],
    )


def _build_emails() -> list[ImportedEmail]:
    return [
        ImportedEmail(
            subject="Hello",
            sender="alice@example.com",
            recipients=["bob@example.com"],
            sent_at=datetime(2026, 3, 13, 10, 5, tzinfo=timezone.utc),
            body_text="Body",
            message_id="msg-1",
            source_folder_path="Mailbox/Inbox",
            attachments=[
                ImportedAttachment(file_name="a.txt", mime_type="text/plain", size_bytes=10)
            ],
        )
    ]


def test_store_persists_run_metadata_and_emails() -> None:
    test_dir = _test_dir()
    try:
        store = _ImportRunStore(test_dir)
        run = _build_run()
        emails = _build_emails()

        saved = store.save(run, emails)

        assert saved.imported_emails[0].message_id == "msg-1"
        assert (test_dir / "run-1.json").exists()
        assert (test_dir / "run-1.emails.json").exists()

        meta_payload = json.loads((test_dir / "run-1.json").read_text(encoding="utf-8"))
        assert meta_payload["import_run_id"] == "run-1"
        assert "imported_emails" not in meta_payload

        email_payload = json.loads((test_dir / "run-1.emails.json").read_text(encoding="utf-8"))
        assert email_payload[0]["message_id"] == "msg-1"
    finally:
        _cleanup(test_dir)


def test_store_loads_runs_after_restart() -> None:
    test_dir = _test_dir()
    try:
        first_store = _ImportRunStore(test_dir)
        run = _build_run("run-2")
        run.status = "finished"
        run.finished_at = datetime(2026, 3, 13, 10, 15, tzinfo=timezone.utc)
        run.email_count = 1
        run.attachment_count = 1
        first_store.save(run, _build_emails())

        second_store = _ImportRunStore(test_dir)
        loaded = second_store.get("run-2")

        assert loaded is not None
        assert loaded.status == "finished"
        assert loaded.email_count == 1
        assert loaded.imported_emails[0].attachments[0].file_name == "a.txt"
    finally:
        _cleanup(test_dir)


def test_update_preserves_existing_emails() -> None:
    test_dir = _test_dir()
    try:
        store = _ImportRunStore(test_dir)
        run = _build_run("run-3")
        store.save(run, _build_emails())

        updated = run.model_copy(update={"status": "failed", "error_message": "boom"})
        result = store.update(updated)

        assert result.imported_emails[0].message_id == "msg-1"
        reloaded = _ImportRunStore(test_dir).get("run-3")
        assert reloaded is not None
        assert reloaded.error_message == "boom"
        assert reloaded.imported_emails[0].message_id == "msg-1"
    finally:
        _cleanup(test_dir)


def test_corrupted_email_file_falls_back_to_empty_email_list() -> None:
    test_dir = _test_dir()
    try:
        run = _build_run("run-4")
        meta_payload = run.model_dump(mode="json", exclude={"imported_emails"})
        (test_dir / "run-4.json").write_text(json.dumps(meta_payload), encoding="utf-8")
        (test_dir / "run-4.emails.json").write_text("{invalid", encoding="utf-8")

        store = _ImportRunStore(test_dir)
        loaded = store.get("run-4")

        assert loaded is not None
        assert loaded.imported_emails == []
        corrupt_files = list(test_dir.glob("run-4.emails.json.corrupt-*"))
        assert len(corrupt_files) == 1
    finally:
        _cleanup(test_dir)


def test_corrupted_metadata_file_is_quarantined_and_skipped() -> None:
    test_dir = _test_dir()
    try:
        (test_dir / "run-5.json").write_text("{invalid", encoding="utf-8")
        (test_dir / "run-5.emails.json").write_text("[]", encoding="utf-8")

        store = _ImportRunStore(test_dir)

        assert store.get("run-5") is None
        corrupt_files = list(test_dir.glob("run-5.json.corrupt-*"))
        assert len(corrupt_files) == 1
    finally:
        _cleanup(test_dir)
