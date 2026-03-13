from datetime import datetime, timezone

import pytest

from app.models.pst_import_models import ImportRun, ImportedAttachment, ImportedEmail
from app.services.pst_import_neo4j_ingest_service import (
    Neo4jBatchIngestError,
    PstImportNeo4jIngestService,
)


class _FakeNeo4jAdapter:
    def __init__(self, *, fail_on_batch_numbers: set[int] | None = None) -> None:
        self.fail_on_batch_numbers = fail_on_batch_numbers or set()
        self.batch_call_count = 0
        self.calls: list[dict] = []

    def execute_write(self, query: str, parameters: dict | None = None) -> list[dict]:
        parameters = parameters or {}
        self.calls.append({"query": query, "parameters": parameters})
        if "emails" in parameters:
            self.batch_call_count += 1
            if self.batch_call_count in self.fail_on_batch_numbers:
                raise RuntimeError(f"boom-batch-{self.batch_call_count}")
        return []


def _build_run() -> ImportRun:
    return ImportRun(
        import_run_id="run-batch",
        source_id="source-1",
        source_path=r"C:\mail\archive.pst",
        selected_node_ids=["node-1"],
        selected_folder_paths=["Mailbox/Inbox"],
        status="running",
        started_at=datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc),
    )


def _build_email(index: int) -> ImportedEmail:
    return ImportedEmail(
        subject=f"Subject {index}",
        sender="alice@example.com",
        recipients=["bob@example.com"],
        sent_at=datetime(2026, 3, 13, 10, index, tzinfo=timezone.utc),
        body_text=f"Body {index}",
        message_id=f"msg-{index}",
        source_folder_path="Mailbox/Inbox",
        attachments=[
            ImportedAttachment(
                file_name=f"attachment-{index}.txt",
                mime_type="text/plain",
                size_bytes=index,
            )
        ],
    )


def test_ingest_run_splits_emails_into_configured_batches() -> None:
    adapter = _FakeNeo4jAdapter()
    service = PstImportNeo4jIngestService(adapter, batch_size=2)
    run = _build_run()
    emails = [_build_email(index) for index in range(1, 6)]

    summary = service.ingest_run(run, emails)

    assert summary.processed_batches == 3
    assert summary.failed_batches == 0
    assert summary.batch_size == 2
    assert run.processed_batches == 3
    assert run.failed_batches == 0
    assert run.batch_size == 2

    batch_sizes = [
        len(call["parameters"]["emails"])
        for call in adapter.calls
        if "emails" in call["parameters"]
    ]
    assert batch_sizes == [2, 2, 1]


def test_ingest_run_aborts_on_first_failed_batch_by_default() -> None:
    adapter = _FakeNeo4jAdapter(fail_on_batch_numbers={2})
    service = PstImportNeo4jIngestService(adapter, batch_size=2, continue_on_batch_error=False)
    run = _build_run()
    emails = [_build_email(index) for index in range(1, 6)]
    progress_updates: list[tuple[int, int, int]] = []

    with pytest.raises(Neo4jBatchIngestError) as exc_info:
        service.ingest_run(
            run,
            emails,
            progress_callback=lambda processed, failed, batch_size: progress_updates.append(
                (processed, failed, batch_size)
            ),
        )

    assert exc_info.value.processed_batches == 1
    assert exc_info.value.failed_batches == 1
    assert exc_info.value.batch_size == 2
    assert progress_updates == [(1, 0, 2), (1, 1, 2)]


def test_ingest_run_can_continue_after_batch_failures() -> None:
    adapter = _FakeNeo4jAdapter(fail_on_batch_numbers={2})
    service = PstImportNeo4jIngestService(adapter, batch_size=2, continue_on_batch_error=True)
    run = _build_run()
    emails = [_build_email(index) for index in range(1, 6)]

    summary = service.ingest_run(run, emails)

    assert summary.processed_batches == 2
    assert summary.failed_batches == 1
    assert run.processed_batches == 2
    assert run.failed_batches == 1
    assert run.batch_size == 2

    run_node_updates = [call for call in adapter.calls if "emails" not in call["parameters"]]
    assert len(run_node_updates) == 2
