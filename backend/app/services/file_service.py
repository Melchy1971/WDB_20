from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from app.models.document_models import DocumentScanResponse, DocumentScanViewItem, ParsedDocument
from app.services import scan_store_service as scan_store
from app.services.document_parser_service import DocumentParserService


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".eml"}
PREVIEW_LIMIT = 400
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileService:
    def __init__(self) -> None:
        self.parser_service = DocumentParserService()

    def scan_supported_files(self, folder_path: str) -> DocumentScanResponse:
        base_path = Path(folder_path).expanduser().resolve()

        if not base_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not base_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")

        scan_id = str(uuid4())
        scan_store.new_scan(scan_id)
        items: list[DocumentScanViewItem] = []

        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue

            extension = file_path.suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                continue

            document_id = str(uuid4())
            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

            # ── Größenlimit ────────────────────────────────────────────────────
            if stat.st_size > MAX_FILE_SIZE_BYTES:
                items.append(DocumentScanViewItem(
                    document_id=document_id,
                    file_name=file_path.name,
                    file_path=str(file_path),
                    extension=extension,
                    mime_type="application/octet-stream",
                    source_type="LOCAL_FOLDER",
                    parser_type="none",
                    preview_text="",
                    content_hash="",
                    last_modified=last_modified,
                    size_bytes=stat.st_size,
                    parse_status="skipped",
                    parse_error=f"Datei überschreitet Größenlimit von {MAX_FILE_SIZE_BYTES} Bytes.",
                ))
                continue

            # ── Parsen — Fehler werden im Parser isoliert, nie globaler Abbruch
            result = self.parser_service.parse_file(file_path)

            if result.parse_status != "parsed":
                items.append(DocumentScanViewItem(
                    document_id=document_id,
                    file_name=file_path.name,
                    file_path=str(file_path),
                    extension=extension,
                    mime_type=result.mime_type,
                    source_type="LOCAL_FOLDER",
                    parser_type=result.parser_type,
                    preview_text="",
                    content_hash="",
                    last_modified=last_modified,
                    size_bytes=stat.st_size,
                    parse_status=result.parse_status,  # "failed" | "unsupported"
                    parse_error=result.parse_error,
                ))
                continue

            # ── Erfolgreich geparstes Dokument ────────────────────────────────
            content_hash = sha256(result.text_content.encode("utf-8")).hexdigest()
            preview_text = result.text_content[:PREVIEW_LIMIT].strip()

            doc = ParsedDocument(
                document_id=document_id,
                scan_id=scan_id,
                file_name=file_path.name,
                file_path=str(file_path),
                extension=extension,
                mime_type=result.mime_type,
                source_type="LOCAL_FOLDER",
                parser_type=result.parser_type,
                preview_text=preview_text,
                text_content=result.text_content,
                content_hash=content_hash,
                last_modified=last_modified,
                size_bytes=stat.st_size,
                parse_status="parsed",
                parse_error=None,
            )
            scan_store.put(scan_id, doc)

            items.append(DocumentScanViewItem(
                document_id=doc.document_id,
                file_name=doc.file_name,
                file_path=doc.file_path,
                extension=doc.extension,
                mime_type=doc.mime_type,
                source_type=doc.source_type,
                parser_type=doc.parser_type,
                preview_text=doc.preview_text,
                content_hash=doc.content_hash,
                last_modified=doc.last_modified,
                size_bytes=doc.size_bytes,
                parse_status=doc.parse_status,
                parse_error=doc.parse_error,
            ))

        return DocumentScanResponse(scan_id=scan_id, items=items)
