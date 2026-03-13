from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.core.config import settings
from app.models.pst_import_models import ImportRun, ImportedEmail

logger = logging.getLogger(__name__)

BatchProgressCallback = Callable[[int, int, int], None]


@dataclass(slots=True)
class Neo4jBatchIngestSummary:
    processed_batches: int
    failed_batches: int
    batch_size: int


class Neo4jBatchIngestError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        processed_batches: int,
        failed_batches: int,
        batch_size: int,
    ) -> None:
        super().__init__(message)
        self.processed_batches = processed_batches
        self.failed_batches = failed_batches
        self.batch_size = batch_size


class PstImportNeo4jIngestService:
    """Persistiert rohe PST-Importdaten in Neo4j, batchweise und fehlertolerant."""

    def __init__(
        self,
        neo4j: Neo4jAdapter | None = None,
        *,
        batch_size: int | None = None,
        continue_on_batch_error: bool | None = None,
    ) -> None:
        self._neo4j = neo4j or Neo4jAdapter()
        configured_batch_size = batch_size or settings.pst_neo4j_batch_size
        self._batch_size = max(1, configured_batch_size)
        if continue_on_batch_error is None:
            continue_on_batch_error = settings.pst_neo4j_continue_on_batch_error
        self._continue_on_batch_error = continue_on_batch_error

    @property
    def batch_size(self) -> int:
        return self._batch_size

    def ingest_run(
        self,
        run: ImportRun,
        emails: list[ImportedEmail],
        *,
        progress_callback: BatchProgressCallback | None = None,
    ) -> Neo4jBatchIngestSummary:
        run.batch_size = self._batch_size
        self._persist_run_node(run, len(emails))

        processed_batches = 0
        failed_batches = 0

        for batch_number, batch in enumerate(self._iter_batches(emails), start=1):
            try:
                self._persist_email_batch(run, batch)
                processed_batches += 1
                logger.info(
                    "Neo4j-Batch persistiert",
                    extra={
                        "import_run_id": run.import_run_id,
                        "batch_number": batch_number,
                        "batch_size": len(batch),
                        "configured_batch_size": self._batch_size,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                failed_batches += 1
                logger.exception(
                    "Neo4j-Batch fehlgeschlagen",
                    extra={
                        "import_run_id": run.import_run_id,
                        "batch_number": batch_number,
                        "batch_size": len(batch),
                        "configured_batch_size": self._batch_size,
                    },
                )
                if progress_callback is not None:
                    progress_callback(processed_batches, failed_batches, self._batch_size)
                if not self._continue_on_batch_error:
                    raise Neo4jBatchIngestError(
                        f"Batch {batch_number} fehlgeschlagen: {exc}",
                        processed_batches=processed_batches,
                        failed_batches=failed_batches,
                        batch_size=self._batch_size,
                    ) from exc
                continue

            if progress_callback is not None:
                progress_callback(processed_batches, failed_batches, self._batch_size)

        run.processed_batches = processed_batches
        run.failed_batches = failed_batches
        run.batch_size = self._batch_size
        self._persist_run_node(run, len(emails))
        return Neo4jBatchIngestSummary(
            processed_batches=processed_batches,
            failed_batches=failed_batches,
            batch_size=self._batch_size,
        )

    def _iter_batches(self, emails: list[ImportedEmail]) -> Iterator[list[ImportedEmail]]:
        if not emails:
            return iter(())
        return (
            emails[index : index + self._batch_size]
            for index in range(0, len(emails), self._batch_size)
        )

    def _persist_run_node(self, run: ImportRun, email_count: int) -> None:
        query = """
        MERGE (r:RawImportRun {importRunId: $import_run_id})
        SET r.sourceId = $source_id,
            r.sourcePath = $source_path,
            r.status = $status,
            r.startedAt = $started_at,
            r.finishedAt = $finished_at,
            r.selectedNodeIds = $selected_node_ids,
            r.selectedFolderPaths = $selected_folder_paths,
            r.emailCount = $email_count,
            r.importedCount = $imported_count,
            r.duplicateCount = $duplicate_count,
            r.attachmentCount = $attachment_count,
            r.processedBatches = $processed_batches,
            r.failedBatches = $failed_batches,
            r.batchSize = $batch_size,
            r.errorMessage = $error_message,
            r.updatedAt = datetime()
        """
        self._neo4j.execute_write(
            query,
            {
                "import_run_id": run.import_run_id,
                "source_id": run.source_id,
                "source_path": run.source_path,
                "status": run.status,
                "started_at": run.started_at.isoformat(),
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "selected_node_ids": run.selected_node_ids,
                "selected_folder_paths": run.selected_folder_paths,
                "email_count": email_count,
                "imported_count": run.imported_count,
                "duplicate_count": run.duplicate_count,
                "attachment_count": run.attachment_count,
                "processed_batches": run.processed_batches,
                "failed_batches": run.failed_batches,
                "batch_size": run.batch_size,
                "error_message": run.error_message,
            },
        )

    def _persist_email_batch(self, run: ImportRun, emails: list[ImportedEmail]) -> None:
        query = """
        MERGE (r:RawImportRun {importRunId: $import_run_id})
        WITH r
        UNWIND $emails AS email
        MERGE (m:RawImportedEmail {
            importRunId: $import_run_id,
            messageId: email.message_id,
            sourceFolderPath: email.source_folder_path
        })
        SET m.sourceId = $source_id,
            m.subject = email.subject,
            m.sender = email.sender,
            m.recipients = email.recipients,
            m.sentAt = email.sent_at,
            m.bodyText = email.body_text,
            m.attachmentCount = size(email.attachments),
            m.updatedAt = datetime()
        MERGE (r)-[:HAS_EMAIL]->(m)
        FOREACH (attachment IN email.attachments |
            MERGE (a:RawImportedAttachment {
                importRunId: $import_run_id,
                messageId: email.message_id,
                sourceFolderPath: email.source_folder_path,
                fileName: attachment.file_name
            })
            SET a.mimeType = attachment.mime_type,
                a.sizeBytes = attachment.size_bytes,
                a.updatedAt = datetime()
            MERGE (m)-[:HAS_ATTACHMENT]->(a)
        )
        """
        self._neo4j.execute_write(
            query,
            {
                "import_run_id": run.import_run_id,
                "source_id": run.source_id,
                "emails": [
                    {
                        "message_id": email.message_id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "recipients": email.recipients,
                        "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                        "body_text": email.body_text,
                        "source_folder_path": email.source_folder_path,
                        "attachments": [
                            {
                                "file_name": attachment.file_name,
                                "mime_type": attachment.mime_type,
                                "size_bytes": attachment.size_bytes,
                            }
                            for attachment in email.attachments
                        ],
                    }
                    for email in emails
                ],
            },
        )
