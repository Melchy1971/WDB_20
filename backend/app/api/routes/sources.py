from fastapi import APIRouter, HTTPException

from app.models.document_models import DocumentScanResponse
from app.models.source_models import (
    CreatePstSourceRequest,
    CreateSourceRequest,
    ListSourcesResponse,
    SelectSourceRequest,
    SelectSourceResponse,
    Source,
)
from app.models.selection_models import (
    SourceSelectionResponse,
    UpdateSourceSelectionRequest,
    UpdateSourceSelectionResponse,
)
from app.models.import_models import ImportPreviewResponse
from app.models.tree_models import SourceTreeResponse
from app.services import import_preview_service
from app.services import pst_parser_service
from app.services import source_registry_service
from app.services import source_selection_service
from app.services.file_service import FileService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=ListSourcesResponse)
def list_sources() -> ListSourcesResponse:
    return ListSourcesResponse(sources=source_registry_service.list_sources())


@router.post("", response_model=Source)
def create_local_folder_source(request: CreateSourceRequest) -> Source:
    return source_registry_service.create_source(request)


@router.post("/pst", response_model=Source)
def create_pst_source(request: CreatePstSourceRequest) -> Source:
    return source_registry_service.create_pst_source(request)


@router.post("/select", response_model=SelectSourceResponse)
def select_source(request: SelectSourceRequest) -> SelectSourceResponse:
    try:
        source = source_registry_service.select_source(request.source_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Quelle nicht gefunden: {request.source_id}",
        )
    return SelectSourceResponse(
        selected_source_id=source.source_id,
        source_type=source.source_type,
    )


@router.get("/{source_id}/tree", response_model=SourceTreeResponse)
def get_source_tree(source_id: str) -> SourceTreeResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    if source.source_type != "PST":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tree-Ansicht ist nur für PST-Quellen verfügbar "
                f"(Quellentyp dieser Quelle: {source.source_type})."
            ),
        )
    try:
        return pst_parser_service.parse_pst_tree(
            pst_path=source.source_path,
            source_id=source_id,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"PST-Parser nicht verfügbar: {exc}",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"PST-Datei konnte nicht gelesen werden: {exc}",
        ) from exc


@router.get("/{source_id}/selection", response_model=SourceSelectionResponse)
def get_selection(source_id: str) -> SourceSelectionResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    return SourceSelectionResponse(
        source_id=source_id,
        selected_node_ids=source_selection_service.get_selection(source_id),
    )


@router.post("/{source_id}/selection", response_model=UpdateSourceSelectionResponse)
def update_selection(
    source_id: str, request: UpdateSourceSelectionRequest
) -> UpdateSourceSelectionResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    saved = source_selection_service.set_selection(source_id, request.selected_node_ids)
    return UpdateSourceSelectionResponse(source_id=source_id, selected_node_ids=saved)


@router.get("/{source_id}/import-preview", response_model=ImportPreviewResponse)
def get_import_preview(source_id: str) -> ImportPreviewResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    if source.source_type != "PST":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Import-Vorschau ist nur für PST-Quellen verfügbar "
                f"(Quellentyp dieser Quelle: {source.source_type})."
            ),
        )
    selected_node_ids = source_selection_service.get_selection(source_id)
    try:
        tree = pst_parser_service.parse_pst_tree(
            pst_path=source.source_path,
            source_id=source_id,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"PST-Parser nicht verfügbar: {exc}",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"PST-Datei konnte nicht gelesen werden: {exc}",
        ) from exc
    return import_preview_service.get_import_preview(source, selected_node_ids, tree.root)


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
    if source.source_type == "PST":
        raise HTTPException(
            status_code=400,
            detail="PST-Import ist noch nicht implementiert.",
        )
    raise HTTPException(
        status_code=400,
        detail=f"Scan für SourceType '{source.source_type}' nicht unterstützt.",
    )
