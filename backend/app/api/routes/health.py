from fastapi import APIRouter

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.core.config import settings
from app.models.system_models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    neo4j_adapter = Neo4jAdapter()
    try:
        neo4j_status = neo4j_adapter.check_connection()
    finally:
        neo4j_adapter.close()

    ollama_status = OllamaAdapter().check_connection()

    document_count = 0
    if neo4j_status == "up":
        try:
            result = neo4j_adapter.execute_read("MATCH (d:Document) RETURN count(d) AS cnt")
            document_count = result[0]["cnt"] if result else 0
        except Exception:
            pass

    return HealthResponse(
        api_status="up",
        neo4j_status=neo4j_status,
        ollama_status=ollama_status,
        environment=settings.app_env,
        document_count=document_count,
    )
