from app.adapters.neo4j_adapter import Neo4jAdapter
from app.models.document_models import ParsedDocument
from app.services import scan_store_service as scan_store


class PersistService:
    def __init__(self) -> None:
        self.neo4j = Neo4jAdapter()

    def persist_by_id(self, scan_id: str, document_id: str) -> str:
        """Lädt das Dokument aus dem Scan-Store und schreibt es nach Neo4j. Gibt file_path zurück."""
        document = scan_store.get(scan_id, document_id)
        if document is None:
            raise KeyError(
                f"Dokument nicht im Scan-Store: scan_id={scan_id}, document_id={document_id}. "
                "Bitte erneut scannen."
            )
        self._write_to_neo4j(document)
        return document.file_path

    def _write_to_neo4j(self, document: ParsedDocument) -> None:
        query = """
        MERGE (d:Document {filePath: $file_path})
        SET d.documentId = $document_id,
            d.fileName = $file_name,
            d.extension = $extension,
            d.mimeType = $mime_type,
            d.sourceType = $source_type,
            d.parserType = $parser_type,
            d.previewText = $preview_text,
            d.textContent = $text_content,
            d.contentHash = $content_hash,
            d.lastModified = $last_modified,
            d.sizeBytes = $size_bytes,
            d.parseStatus = $parse_status,
            d.createdAt = datetime()
        RETURN d.filePath AS filePath
        """
        self.neo4j.execute_write(query, {
            "document_id": document.document_id,
            "file_path": document.file_path,
            "file_name": document.file_name,
            "extension": document.extension,
            "mime_type": document.mime_type,
            "source_type": document.source_type,
            "parser_type": document.parser_type,
            "preview_text": document.preview_text,
            "text_content": document.text_content,
            "content_hash": document.content_hash,
            "last_modified": document.last_modified,
            "size_bytes": document.size_bytes,
            "parse_status": document.parse_status,
        })
