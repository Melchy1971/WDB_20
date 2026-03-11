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

    return HealthResponse(
        api_status="up",
        neo4j_status=neo4j_status,
        ollama_status=ollama_status,
        environment=settings.app_env,
    )
