from fastapi import APIRouter, HTTPException

from app.models.document_models import Document, PersistDocumentResponse
from app.services.persist_service import PersistService

router = APIRouter(prefix="/persist", tags=["persist"])


@router.post("/document", response_model=PersistDocumentResponse)
def persist_document(document: Document) -> PersistDocumentResponse:
    try:
        PersistService.persist_document(document)
        return PersistDocumentResponse(status="stored", file_path=document.file_path)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not persist document") from exc
