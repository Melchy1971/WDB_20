from fastapi import APIRouter, HTTPException

<<<<<<< HEAD
from app.models.document_models import DocumentScanResponse
from app.models.source_models import FolderScanRequest
=======
from app.models.document_models import DocumentItem, DocumentListResponse
from app.models.source_models import FolderSourceRequest
>>>>>>> a19e3da ( Changes to be committed:)
from app.services.file_service import FileService

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/folder/scan", response_model=DocumentScanResponse)
def scan_folder(request: FolderScanRequest) -> DocumentScanResponse:
    try:
<<<<<<< HEAD
        documents = FileService.scan_txt_files(request.folder_path)
        return DocumentScanResponse(items=documents)
=======
        parsed_items = service.scan_supported_files(request.folder_path)

        items = [
            DocumentItem(
                file_name=item.file_name,
                file_path=item.file_path,
                extension=item.extension,
                mime_type=item.mime_type,
                source_type=item.source_type,
                parser_type=item.parser_type,
                preview_text=item.preview_text,
                text_content=item.text_content,
                content_hash=item.content_hash,
                last_modified=item.last_modified,
                size_bytes=item.size_bytes,
                parse_status=item.parse_status,
            )
            for item in parsed_items
        ]

        return DocumentListResponse(items=items)
>>>>>>> a19e3da ( Changes to be committed:)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not scan folder") from exc
