from fastapi import APIRouter, HTTPException

from app.models.document_models import DocumentScanResponse
from app.models.source_models import CreateSourceRequest, ListSourcesResponse, Source
from app.services import source_registry_service
from app.services.file_service import FileService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=ListSourcesResponse)
def list_sources() -> ListSourcesResponse:
    return ListSourcesResponse(sources=source_registry_service.list_sources())


@router.post("", response_model=Source)
def create_source(request: CreateSourceRequest) -> Source:
    return source_registry_service.create_source(request)


@router.post("/{source_id}/scan", response_model=DocumentScanResponse)
def scan_source(source_id: str) -> DocumentScanResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    if source.source_type == "LOCAL_FOLDER":
        try:
            service = FileService()
            return service.scan_supported_files(source.source_path)
        except (FileNotFoundError, NotADirectoryError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Fehler beim Scannen") from exc
    raise HTTPException(
        status_code=400,
        detail=f"Scan für SourceType '{source.source_type}' noch nicht implementiert.",
    )
