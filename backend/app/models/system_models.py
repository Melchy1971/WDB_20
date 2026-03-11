from pydantic import BaseModel


class HealthResponse(BaseModel):
    api_status: str
    neo4j_status: str
    ollama_status: str
    environment: str


class FolderSourceRequest(BaseModel):
    folder_path: str


class DocumentItem(BaseModel):
    file_name: str
    file_path: str
    extension: str
    text_content: str
    content_hash: str
    last_modified: str
    size_bytes: int


class DocumentListResponse(BaseModel):
    items: list[DocumentItem]


class PersistDocumentRequest(BaseModel):
    file_name: str
    file_path: str
    extension: str
    text_content: str
    content_hash: str
    last_modified: str
    size_bytes: int


class PersistDocumentResponse(BaseModel):
    status: str
    file_path: str
