from pydantic import BaseModel


class Document(BaseModel):
    """Internes Modell mit vollem Textinhalt — wird nicht ans Frontend geliefert."""
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


class DocumentScanItem(BaseModel):
    """Scan-Ergebnis für das Frontend — kein text_content."""
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
    parse_status: str


class DocumentScanResponse(BaseModel):
    items: list[DocumentScanItem]


class PersistDocumentRequest(BaseModel):
    """Vollständiges Dokument für die Neo4j-Persistierung."""
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


class PersistByHashRequest(BaseModel):
    content_hash: str


class PersistDocumentResponse(BaseModel):
    status: str
    file_path: str
