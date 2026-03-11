import httpx

from app.core.config import settings


class OllamaAdapter:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")

    def check_connection(self) -> str:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return "up" if response.status_code == 200 else "down"
        except Exception:
            return "down"
