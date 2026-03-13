import logging

from fastapi import APIRouter, HTTPException

from app.adapters.pst_archive_adapter import PstError
from app.models.analysis_models import ScanAnalysisResponse
from app.models.document_models import DocumentScanResponse
from app.models.import_models import ImportPreviewResponse
from app.models.selection_models import (
    SourceSelectionResponse,
    UpdateSourceSelectionRequest,
    UpdateSourceSelectionResponse,
)
from app.models.source_models import (
    CreatePstSourceRequest,
    CreateSourceRequest,
    ListSourcesResponse,
    SelectSourceRequest,
    SelectSourceResponse,
    Source,
    UpdateSourcePathRequest,
)
from app.models.tree_models import PstTreeRequest, SourceTreeResponse
from app.services import import_preview_service
from app.services import scan_store_service
from app.services import source_registry_service
from app.services import source_selection_service
from app.services.analysis_provider_service import get_analysis_provider_service
from app.services.file_service import FileService
from app.services.pst_access_service import validate_pst_path
from app.services.pst_parser_service import PstParserService
from app.services.settings_service import NoActiveAiProviderError

router = APIRouter(prefix="/sources", tags=["sources"])
logger = logging.getLogger(__name__)


def _raise_pst_http_error(exc: PstError, pst_path: str, source_id: str | None = None) -> HTTPException:
    logger.warning(
        "PST-Operation fehlgeschlagen",
        extra={"pst_path": pst_path, "source_id": source_id, "pst_error_code": exc.code},
        exc_info=exc,
    )
    return HTTPException(status_code=exc.status_code, detail=exc.to_client_detail())


def _build_pst_tree_or_raise(pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
    try:
        return PstParserService.build_tree(
            pst_path=pst_path,
            source_id=source_id,
        )
    except PstError as exc:
        raise _raise_pst_http_error(exc, pst_path=pst_path, source_id=source_id) from exc


def _validate_pst_source_path_or_raise(pst_path: str) -> None:
    try:
        validate_pst_path(pst_path)
    except PstError as exc:
        raise _raise_pst_http_error(exc, pst_path=pst_path) from exc


@router.get("", response_model=ListSourcesResponse)
def list_sources() -> ListSourcesResponse:
    return ListSourcesResponse(sources=source_registry_service.list_sources())


@router.post("", response_model=Source)
def create_local_folder_source(request: CreateSourceRequest) -> Source:
    return source_registry_service.create_source(request)


@router.post("/pst", response_model=Source)
def create_pst_source(request: CreatePstSourceRequest) -> Source:
    _validate_pst_source_path_or_raise(request.pst_file_path)
    return source_registry_service.create_pst_source(request)


@router.get("/pst/tree", response_model=SourceTreeResponse)
def get_pst_tree_by_path(path: str) -> SourceTreeResponse:
    return _build_pst_tree_or_raise(pst_path=path)


@router.post("/pst/tree", response_model=SourceTreeResponse)
def post_pst_tree_by_path(request: PstTreeRequest) -> SourceTreeResponse:
    return _build_pst_tree_or_raise(pst_path=request.path)


@router.get("/selected", response_model=SelectSourceResponse | None)
def get_selected_source() -> SelectSourceResponse | None:
    source_id = source_registry_service.get_selected_source_id()
    if source_id is None:
        return None
    source = source_registry_service.get_source(source_id)
    if source is None:
        return None
    return SelectSourceResponse(
        selected_source_id=source.source_id,
        source_type=source.source_type,
    )


@router.delete("/{source_id}", response_model=Source)
def delete_source(source_id: str) -> Source:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")
    source_registry_service.delete_source(source_id)
    return source


@router.patch("/{source_id}/path", response_model=Source)
def update_source_path(source_id: str, request: UpdateSourcePathRequest) -> Source:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")

    source_path = request.source_path.strip()
    if source.source_type == "PST":
        _validate_pst_source_path_or_raise(source_path)

    try:
        return source_registry_service.update_source_path(source_id, source_path)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")


@router.post("/select", response_model=SelectSourceResponse)
def select_source(request: SelectSourceRequest) -> SelectSourceResponse:
    source = source_registry_service.get_source(request.source_id)
    if source is None:
        raise HTTPException(
            status_code=404,
            detail=f"Quelle nicht gefunden: {request.source_id}",
        )
    if source.source_type == "PST":
        _validate_pst_source_path_or_raise(source.source_path)

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
    return _build_pst_tree_or_raise(pst_path=source.source_path, source_id=source_id)


@router.get("/{source_id}/selection", response_model=SourceSelectionResponse)
def get_selection(source_id: str) -> SourceSelectionResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")

    if source.source_type == "PST":
        tree = _build_pst_tree_or_raise(pst_path=source.source_path, source_id=source_id)
        selection = source_selection_service.sanitize_selection_for_tree(source_id, tree)
    else:
        selection = source_selection_service.get_selection_record(source_id)

    return SourceSelectionResponse(
        source_id=source_id,
        selected_node_ids=selection.selected_node_ids,
        selected_folder_paths=selection.selected_folder_paths,
        selected_count=len(selection.selected_node_ids),
    )


@router.post("/{source_id}/selection", response_model=UpdateSourceSelectionResponse)
def update_selection(
    source_id: str, request: UpdateSourceSelectionRequest
) -> UpdateSourceSelectionResponse:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")

    if source.source_type == "PST":
        tree = _build_pst_tree_or_raise(pst_path=source.source_path, source_id=source_id)
        selection = source_selection_service.set_selection_for_tree(
            source_id=source_id,
            node_ids=request.selected_node_ids,
            tree=tree,
        )
        selected_node_ids = selection.selected_node_ids
    else:
        selected_node_ids = source_selection_service.set_selection(source_id, request.selected_node_ids)
        selection = source_selection_service.get_selection_record(source_id)

    return UpdateSourceSelectionResponse(
        source_id=source_id,
        selected_node_ids=selected_node_ids,
        selected_folder_paths=selection.selected_folder_paths,
        selected_count=len(selected_node_ids),
    )


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
    tree = _build_pst_tree_or_raise(pst_path=source.source_path, source_id=source_id)
    valid_node_ids = PstParserService.collect_valid_node_ids(tree)
    selected_node_ids = source_selection_service.sanitize_selection(source_id, valid_node_ids)
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


@router.post("/scan-analysis/{scan_id}", response_model=ScanAnalysisResponse)
def analyze_scan(scan_id: str) -> ScanAnalysisResponse:
    documents = scan_store_service.list_documents(scan_id)
    if not documents:
        raise HTTPException(status_code=404, detail=f"Scan nicht gefunden oder keine Dokumente: {scan_id}")
    parsed_docs = [d for d in documents if d.parse_status == "parsed"]
    if not parsed_docs:
        raise HTTPException(status_code=422, detail="Keine erfolgreich geparsten Dokumente im Scan.")
    try:
        results = get_analysis_provider_service().analyze_documents(scan_id=scan_id, documents=parsed_docs)
    except NoActiveAiProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"KI-Analyse fehlgeschlagen: {exc}") from exc
    return ScanAnalysisResponse(scan_id=scan_id, results=results)
