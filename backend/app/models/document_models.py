from typing import Literal

from pydantic import BaseModel

ParseStatus = Literal["parsed", "failed", "skipped", "unsupported"]


class ParsedDocument(BaseModel):
    """Internes Modell mit vollem Textinhalt — wird nie ans Frontend geliefert."""
    document_id: str
    scan_id: str
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
    parse_status: ParseStatus
    parse_error: str | None = None


class DocumentScanViewItem(BaseModel):
    """ViewModel für das Frontend — kein text_content."""
    document_id: str
    file_name: str
    file_path: str
    extension: str
    mime_type: str
    source_type: str
    parser_type: str
    preview_text: str
    content_hash: str
    last_modified: str
    size_bytes: int
    parse_status: ParseStatus
    parse_error: str | None = None


class DocumentScanResponse(BaseModel):
    scan_id: str
    items: list[DocumentScanViewItem]
