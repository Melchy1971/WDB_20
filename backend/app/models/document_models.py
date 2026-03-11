from datetime import datetime

from pydantic import BaseModel, Field


class Document(BaseModel):
    file_name: str
    file_path: str
    extension: str
    mime_type: str
    source_type: str
    parser_type: str
    preview_text: str
    text_content: str
    content_hash: str
<<<<<<< HEAD
    last_modified: datetime
    size_bytes: int = Field(..., ge=0)


class DocumentScanResponse(BaseModel):
    items: list[Document]
=======
    last_modified: str
    size_bytes: int
    parse_status: str


class DocumentListResponse(BaseModel):
    items: list[DocumentItem]


class PersistDocumentRequest(BaseModel):
    file_name: str
    file_path: str
    extension: str
    mime_type: str
    source_type: str
    parser_type: str
    preview_text: str
    text_content: str
    content_hash: str
    last_modified: str
    size_bytes: int
    parse_status: str
>>>>>>> a19e3da ( Changes to be committed:)


class PersistDocumentResponse(BaseModel):
    status: str
    file_path: str
