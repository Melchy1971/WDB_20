from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from app.models.document_models import Document, DocumentScanItem
from app.services import scan_store
from app.services.document_parser_service import DocumentParserService


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".eml"}
PREVIEW_LIMIT = 400
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileService:
    def __init__(self) -> None:
        self.parser_service = DocumentParserService()

    def scan_supported_files(self, folder_path: str) -> list[DocumentScanItem]:
        base_path = Path(folder_path).expanduser().resolve()

        if not base_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not base_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")

        scan_store.clear()
        items: list[DocumentScanItem] = []

        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue

            extension = file_path.suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                continue

            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

            if stat.st_size > MAX_FILE_SIZE_BYTES:
                items.append(DocumentScanItem(
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
                    parse_status="skipped_too_large",
                ))
                continue

            try:
                text_content, mime_type, parser_type, parse_status = self.parser_service.parse_file(file_path)
            except Exception:
                items.append(DocumentScanItem(
                    file_name=file_path.name,
                    file_path=str(file_path),
                    extension=extension,
                    mime_type="application/octet-stream",
                    source_type="LOCAL_FOLDER",
                    parser_type="error",
                    preview_text="",
                    content_hash="",
                    last_modified=last_modified,
                    size_bytes=stat.st_size,
                    parse_status="parse_error",
                ))
                continue

            content_hash = sha256(text_content.encode("utf-8")).hexdigest()
            preview_text = text_content[:PREVIEW_LIMIT].strip()

            doc = Document(
                file_name=file_path.name,
                file_path=str(file_path),
                extension=extension,
                mime_type=mime_type,
                source_type="LOCAL_FOLDER",
                parser_type=parser_type,
                preview_text=preview_text,
                text_content=text_content,
                content_hash=content_hash,
                last_modified=last_modified,
                size_bytes=stat.st_size,
                parse_status=parse_status,
            )
            scan_store.put(doc)

            items.append(DocumentScanItem(
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
            ))

        return items
