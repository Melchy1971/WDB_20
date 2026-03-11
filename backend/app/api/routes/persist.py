from fastapi import APIRouter, HTTPException

from app.models.document_models import PersistByHashRequest, PersistDocumentRequest, PersistDocumentResponse
from app.services import scan_store
from app.services.persist_service import PersistService

router = APIRouter(prefix="/persist", tags=["persist"])


@router.post("/document", response_model=PersistDocumentResponse)
def persist_document(request: PersistByHashRequest) -> PersistDocumentResponse:
    document = scan_store.get(request.content_hash)
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Dokument nicht im Scan-Store. Bitte erneut scannen.",
        )
    try:
        service = PersistService()
        service.persist_document(PersistDocumentRequest(**document.model_dump()))
        return PersistDocumentResponse(status="stored", file_path=document.file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not persist document") from exc
