from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ImportRunStatus = Literal["queued", "running", "finished", "failed"]


class ImportedAttachment(BaseModel):
    file_name: str
    mime_type: str | None = None
    size_bytes: int | None = None


class ImportedEmail(BaseModel):
    subject: str | None = None
    sender: str | None = None
    recipients: list[str] = Field(default_factory=list)
    sent_at: datetime | None = None
    body_text: str
    message_id: str
    source_folder_path: str
    attachments: list[ImportedAttachment] = Field(default_factory=list)


class ImportRun(BaseModel):
    import_run_id: str
    source_id: str
    source_path: str
    selected_node_ids: list[str] = Field(default_factory=list)
    selected_folder_paths: list[str] = Field(default_factory=list)
    status: ImportRunStatus
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None
    email_count: int = 0
    attachment_count: int = 0
    imported_emails: list[ImportedEmail] = Field(default_factory=list)


class ImportRunResponse(BaseModel):
    import_run_id: str
    source_id: str
    selected_node_ids: list[str] = Field(default_factory=list)
    email_count: int
    attachment_count: int
    error_message: str | None = None
    status: ImportRunStatus
    imported_emails: list[ImportedEmail] = Field(default_factory=list)
