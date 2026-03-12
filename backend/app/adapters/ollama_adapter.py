import httpx
import json

from app.core.config import settings
from app.models.analysis_models import AnalysisResult
from app.models.pst_import_models import ImportedEmail


class OllamaAdapter:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def check_connection(self) -> str:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return "up" if response.status_code == 200 else "down"
        except Exception:
            return "down"

    def analyze_import_run(
        self,
        import_run_id: str,
        emails: list[ImportedEmail],
    ) -> list[AnalysisResult]:
        prompt = self._build_prompt(import_run_id, emails)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        response = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=120.0)
        response.raise_for_status()
        body = response.json()
        text = str(body.get("response", "")).strip()
        if not text:
            raise RuntimeError("Ollama lieferte keine Analyseantwort.")

        parsed = self._parse_results(text)
        return [AnalysisResult.model_validate(item) for item in parsed]

    def _build_prompt(self, import_run_id: str, emails: list[ImportedEmail]) -> str:
        emails_payload = [
            {
                "message_id": email.message_id,
                "subject": email.subject,
                "sender": email.sender,
                "recipients": email.recipients,
                "source_folder_path": email.source_folder_path,
                "body_text": email.body_text,
            }
            for email in emails
        ]
        schema = {
            "results": [
                {
                    "topic_label": "string",
                    "summary": "string",
                    "keywords": ["string"],
                    "entities": ["string"],
                    "priority": "low|medium|high",
                    "confidence": 0.0,
                }
            ]
        }
        return (
            "Analysiere die folgenden E-Mails eines PST-Imports und liefere NUR valides JSON "
            "im exakt angegebenen Schema. Keine Markdown-Ausgabe. "
            f"ImportRun-ID: {import_run_id}. "
            f"Schema: {json.dumps(schema, ensure_ascii=False)}. "
            f"E-Mails: {json.dumps(emails_payload, ensure_ascii=False)}"
        )

    def _parse_results(self, text: str) -> list[dict]:
        normalized = text.strip()
        if normalized.startswith("```"):
            normalized = normalized.strip("`")
            if normalized.startswith("json"):
                normalized = normalized[4:].strip()

        try:
            decoded = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama lieferte kein parsebares JSON für Analyseergebnisse.") from exc

        if isinstance(decoded, dict) and isinstance(decoded.get("results"), list):
            return decoded["results"]
        if isinstance(decoded, list):
            return decoded
        raise RuntimeError("Ollama-Antwort enthält kein gültiges Ergebnisarray.")
