from pydantic import BaseModel


class PersistDocumentByIdRequest(BaseModel):
    """Persistierungsanfrage über scan_id + document_id — kein Dokumentpayload."""
    scan_id: str
    document_id: str


class PersistDocumentResponse(BaseModel):
    status: str
    file_path: str
