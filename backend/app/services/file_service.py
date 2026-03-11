from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

<<<<<<< HEAD
from app.models.document_models import Document


class FileService:
    @staticmethod
    def scan_txt_files(folder_path: str) -> list[Document]:
        base_path = Path(folder_path).expanduser().resolve()
=======
from app.models.ingestion_models import ParsedDocument
from app.services.document_parser_service import DocumentParserService


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".eml"}
PREVIEW_LIMIT = 400


class FileService:
    def __init__(self) -> None:
        self.parser_service = DocumentParserService()

    def scan_supported_files(self, folder_path: str) -> list[ParsedDocument]:
        base_path = Path(folder_path)
>>>>>>> a19e3da ( Changes to be committed:)

        if not base_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not base_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")

<<<<<<< HEAD
        documents: list[Document] = []

        for file_path in base_path.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() != ".txt":
                continue

            text_content = file_path.read_text(encoding="utf-8", errors="ignore")
=======
        items: list[ParsedDocument] = []

        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue

            extension = file_path.suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                continue

>>>>>>> a19e3da ( Changes to be committed:)
            stat = file_path.stat()
            text_content, mime_type, parser_type, parse_status = self.parser_service.parse_file(file_path)

            preview_text = text_content[:PREVIEW_LIMIT].strip()

<<<<<<< HEAD
            documents.append(
                Document(
=======
            items.append(
                ParsedDocument(
>>>>>>> a19e3da ( Changes to be committed:)
                    file_name=file_path.name,
                    file_path=str(file_path),
                    extension=extension,
                    mime_type=mime_type,
                    source_type="LOCAL_FOLDER",
                    parser_type=parser_type,
                    preview_text=preview_text,
                    text_content=text_content,
                    content_hash=sha256(text_content.encode("utf-8")).hexdigest(),
                    last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                    size_bytes=stat.st_size,
                    parse_status=parse_status,
                )
            )

        return documents
