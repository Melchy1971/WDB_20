import json
from typing import Any, cast
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.models.analysis_models import AnalysisPriority
from app.models.analysis_models import AnalysisResult
from app.models.pst_import_models import ImportedEmail


class DnaBotAdapter:
    def __init__(self) -> None:
        self.base_url = settings.dnabot_base_url.rstrip("/")
        self.model = settings.dnabot_model
        self.api_key = settings.dnabot_api_key

    def check_connection(self) -> str:
        if not self.base_url:
            return "down"
        request = Request(f"{self.base_url}/health", method="GET")
        try:
            with urlopen(request, timeout=5.0) as response:  # noqa: S310
                return "up" if response.status == 200 else "down"
        except Exception:
            return "down"

    def analyze_import_run(
        self,
        import_run_id: str,
        emails: list[ImportedEmail],
    ) -> list[AnalysisResult]:
        payload: dict[str, Any] = {
            "model": self.model,
            "import_run_id": import_run_id,
            "emails": [
                {
                    "message_id": email.message_id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "recipients": email.recipients,
                    "source_folder_path": email.source_folder_path,
                    "body_text": email.body_text,
                }
                for email in emails
            ],
        }

        raw_body = self._post_json("/v1/import-run-analysis", payload)
        body_raw: Any = json.loads(raw_body)
        if not isinstance(body_raw, dict):
            raise RuntimeError("DNAbot lieferte kein gültiges JSON-Objekt.")
        body = cast(dict[str, Any], body_raw)

        results_raw = body.get("results")
        if not isinstance(results_raw, list):
            raise RuntimeError("DNAbot lieferte kein gültiges 'results'-Array.")
        results: list[dict[str, Any]] = []
        for raw_item in cast(list[Any], results_raw):
            if isinstance(raw_item, dict):
                results.append(cast(dict[str, Any], raw_item))

        return [
            AnalysisResult(
                topic_label=str(item.get("topic_label", "")),
                summary=str(item.get("summary", "")),
                keywords=[str(x) for x in item.get("keywords", []) if isinstance(x, str)],
                entities=[str(x) for x in item.get("entities", []) if isinstance(x, str)],
                priority=self._normalize_priority(item.get("priority")),
                confidence=float(item.get("confidence", 0.0)),
            )
            for item in results
        ]

    def _post_json(self, path: str, payload: dict[str, Any]) -> str:
        if not self.base_url:
            raise RuntimeError("DNAbot Base-URL ist nicht konfiguriert.")

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = Request(
            url=f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=120.0) as response:  # noqa: S310
                status = response.status
                response_body = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"DNAbot-Request fehlgeschlagen: {exc}") from exc

        if status >= 400:
            raise RuntimeError(f"DNAbot antwortete mit HTTP {status}: {response_body}")

        return response_body

    def _normalize_priority(self, raw_value: object) -> AnalysisPriority:
        if raw_value in {"low", "medium", "high"}:
            return cast(AnalysisPriority, raw_value)
        return "medium"
