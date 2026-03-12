from __future__ import annotations

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.models.pst_import_models import ImportRun, ImportedEmail


class PstImportNeo4jIngestService:
    """Persistiert rohe PST-Importdaten in Neo4j."""

    def __init__(self) -> None:
        self._neo4j = Neo4jAdapter()

    def ingest_run(self, run: ImportRun, emails: list[ImportedEmail]) -> None:
        self._persist_run_node(run, len(emails))
        for email in emails:
            self._persist_email_with_attachments(run, email)

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
            r.attachmentCount = $attachment_count,
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
                "attachment_count": run.attachment_count,
                "error_message": run.error_message,
            },
        )

    def _persist_email_with_attachments(self, run: ImportRun, email: ImportedEmail) -> None:
        query = """
        MERGE (r:RawImportRun {importRunId: $import_run_id})
        MERGE (m:RawImportedEmail {importRunId: $import_run_id, messageId: $message_id})
        SET m.sourceId = $source_id,
            m.subject = $subject,
            m.sender = $sender,
            m.recipients = $recipients,
            m.sentAt = $sent_at,
            m.bodyText = $body_text,
            m.sourceFolderPath = $source_folder_path,
            m.attachmentCount = $attachment_count,
            m.updatedAt = datetime()
        MERGE (r)-[:HAS_EMAIL]->(m)
        WITH m
        UNWIND $attachments AS attachment
        MERGE (a:RawImportedAttachment {
            importRunId: $import_run_id,
            messageId: $message_id,
            fileName: attachment.file_name
        })
        SET a.mimeType = attachment.mime_type,
            a.sizeBytes = attachment.size_bytes,
            a.updatedAt = datetime()
        MERGE (m)-[:HAS_ATTACHMENT]->(a)
        """
        self._neo4j.execute_write(
            query,
            {
                "import_run_id": run.import_run_id,
                "source_id": run.source_id,
                "message_id": email.message_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipients": email.recipients,
                "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                "body_text": email.body_text,
                "source_folder_path": email.source_folder_path,
                "attachment_count": len(email.attachments),
                "attachments": [
                    {
                        "file_name": attachment.file_name,
                        "mime_type": attachment.mime_type,
                        "size_bytes": attachment.size_bytes,
                    }
                    for attachment in email.attachments
                ],
            },
        )
