from pydantic import BaseModel


class HealthResponse(BaseModel):
    api_status: str
    neo4j_status: str
    ollama_status: str
    environment: str
