from fastapi import APIRouter, HTTPException

from app.models.document_models import DocumentScanResponse
from app.models.source_models import FolderScanRequest
from app.services.file_service import FileService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/folder/scan", response_model=DocumentScanResponse)
def scan_folder(request: FolderScanRequest) -> DocumentScanResponse:
    try:
        service = FileService()
        documents = service.scan_supported_files(request.folder_path)
        return DocumentScanResponse(items=documents)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not scan folder") from exc
