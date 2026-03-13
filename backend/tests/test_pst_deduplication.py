from datetime import datetime, timezone

from app.models.pst_import_models import ImportRun, ImportedEmail
from app.services.pst_import_service import (
    NoOpDuplicateMessageRegistry,
    build_dedup_key,
)


def _run() -> ImportRun:
    return ImportRun(
        import_run_id="run-dedup",
        source_id="source-1",
        source_path=r"C:\mail\archive.pst",
        selected_node_ids=["node-1"],
        selected_folder_paths=["Mailbox/Inbox"],
        status="running",
        started_at=datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc),
    )


def _email(
    *,
    message_id: str,
    subject: str = "Subject",
    sender: str = "alice@example.com",
    sent_at: datetime | None = None,
    body_text: str = "Body text",
) -> ImportedEmail:
    return ImportedEmail(
        subject=subject,
        sender=sender,
        recipients=["bob@example.com"],
        sent_at=sent_at or datetime(2026, 3, 13, 10, 5, tzinfo=timezone.utc),
        body_text=body_text,
        message_id=message_id,
        source_folder_path="Mailbox/Inbox",
        attachments=[],
    )


def test_build_dedup_key_prefers_message_id() -> None:
    email = _email(message_id="<abc@example.com>")
    assert build_dedup_key(email) == "message-id:<abc@example.com>"


def test_build_dedup_key_falls_back_to_deterministic_hash() -> None:
    email_a = _email(message_id="", body_text="Hello world")
    email_b = _email(message_id="", body_text="Hello world")
    assert build_dedup_key(email_a).startswith("fallback:")
    assert build_dedup_key(email_a) == build_dedup_key(email_b)


def test_run_model_tracks_duplicate_and_imported_counts() -> None:
    run = _run()
    run.imported_count = 4
    run.duplicate_count = 2
    assert run.imported_count == 4
    assert run.duplicate_count == 2


def test_cross_run_registry_hook_is_noop_by_default() -> None:
    registry = NoOpDuplicateMessageRegistry()
    assert registry.is_duplicate(build_dedup_key(_email(message_id="x")), _email(message_id="x"), _run()) is False
