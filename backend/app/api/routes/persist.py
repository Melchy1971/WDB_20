from fastapi import APIRouter, HTTPException

from app.models.ingestion_models import PersistDocumentByIdRequest, PersistDocumentResponse
from app.services.persist_service import PersistService

router = APIRouter(prefix="/persist", tags=["persist"])


@router.post("/document", response_model=PersistDocumentResponse)
def persist_document(request: PersistDocumentByIdRequest) -> PersistDocumentResponse:
    try:
        service = PersistService()
        file_path = service.persist_by_id(request.scan_id, request.document_id)
        return PersistDocumentResponse(status="stored", file_path=file_path)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not persist document") from exc
