from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ConfigurationError, Neo4jError, ServiceUnavailable

from app.core.config import settings


class Neo4jAdapter:
    def __init__(self, uri: str | None = None, user: str | None = None, password: str | None = None) -> None:
        self._driver = GraphDatabase.driver(
            uri or settings.neo4j_uri,
            auth=(user or settings.neo4j_user, password or settings.neo4j_password),
        )

    def check_connection(self) -> str:
        try:
            self._driver.verify_connectivity()
            return "up"
        except (ServiceUnavailable, AuthError, ConfigurationError, Neo4jError):
            return "down"
        except Exception:
            return "down"

    def close(self) -> None:
        self._driver.close()

    def upsert_document(
        self,
        file_path: str,
        file_name: str,
        extension: str,
        text_content: str,
        content_hash: str,
        last_modified: str,
        size_bytes: int,
    ):
        query = """
MERGE (d:Document {filePath: $filePath})
SET d.fileName = $fileName,
    d.filePath = $filePath,
    d.extension = $extension,
    d.textContent = $textContent,
    d.contentHash = $contentHash,
    d.lastModified = $lastModified,
    d.sizeBytes = $sizeBytes,
    d.createdAt = datetime()
RETURN d
"""

        with self._driver.session() as session:
            result = session.run(
                query,
                filePath=file_path,
                fileName=file_name,
                extension=extension,
                textContent=text_content,
                contentHash=content_hash,
                lastModified=last_modified,
                sizeBytes=size_bytes,
            )
            return result.single()
