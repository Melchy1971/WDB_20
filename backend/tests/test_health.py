from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["api_status"] == "up"
    assert data["neo4j_status"] in {"up", "down"}
    assert data["ollama_status"] in {"up", "down"}
    assert data["environment"]
