from neo4j.exceptions import Neo4jError

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.models.document_models import Document


class PersistService:
    @staticmethod
    def persist_document(document: Document) -> None:
        adapter = Neo4jAdapter()

<<<<<<< HEAD
        try:
            adapter.upsert_document(
=======
        query = """
        MERGE (d:Document {filePath: $file_path})
        SET d.fileName = $file_name,
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
        RETURN d
        """

        with adapter._driver.session() as session:
            session.run(
                query,
>>>>>>> a19e3da ( Changes to be committed:)
                file_path=document.file_path,
                file_name=document.file_name,
                extension=document.extension,
                mime_type=document.mime_type,
                source_type=document.source_type,
                parser_type=document.parser_type,
                preview_text=document.preview_text,
                text_content=document.text_content,
                content_hash=document.content_hash,
                last_modified=document.last_modified.isoformat(),
                size_bytes=document.size_bytes,
<<<<<<< HEAD
            )
        except Neo4jError as exc:
            raise RuntimeError("Neo4j persistence failed") from exc
        finally:
            adapter.close()
=======
                parse_status=document.parse_status,
            ).single()
>>>>>>> a19e3da ( Changes to be committed:)
