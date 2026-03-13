import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.source_models import CreatePstSourceRequest, CreateSourceRequest, Source

_PERSIST_FILE = Path(__file__).resolve().parents[3] / "data" / "sources.json"


class _SourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, Source] = {}
        self._selected_source_id: str | None = None
        self._load()

    def _load(self) -> None:
        if not _PERSIST_FILE.exists():
            return
        try:
            data = json.loads(_PERSIST_FILE.read_text(encoding="utf-8"))
            for s in data.get("sources", []):
                source = Source(**s)
                self._sources[source.source_id] = source
            self._selected_source_id = data.get("selected_source_id")
        except Exception:
            pass

    def _save(self) -> None:
        _PERSIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "sources": [s.model_dump() for s in self._sources.values()],
            "selected_source_id": self._selected_source_id,
        }
        _PERSIST_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def list_sources(self) -> list[Source]:
        return list(self._sources.values())

    def create_source(self, request: CreateSourceRequest) -> Source:
        source = Source(
            source_id=str(uuid4()),
            source_type=request.source_type,
            label=request.label,
            source_path=request.source_path,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._sources[source.source_id] = source
        self._save()
        return source

    def create_pst_source(self, request: CreatePstSourceRequest) -> Source:
        source = Source(
            source_id=str(uuid4()),
            source_type="PST",
            label=request.label,
            source_path=request.pst_file_path,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._sources[source.source_id] = source
        self._save()
        return source

    def get_source(self, source_id: str) -> Source | None:
        return self._sources.get(source_id)

    def update_source_path(self, source_id: str, source_path: str) -> Source:
        source = self._sources.get(source_id)
        if source is None:
            raise KeyError(source_id)

        updated = source.model_copy(update={"source_path": source_path})
        self._sources[source_id] = updated
        self._save()
        return updated

    def select_source(self, source_id: str) -> Source:
        source = self._sources.get(source_id)
        if source is None:
            raise KeyError(source_id)
        self._selected_source_id = source_id
        self._save()
        return source

    def get_selected_source_id(self) -> str | None:
        return self._selected_source_id

    def delete_source(self, source_id: str) -> None:
        self._sources.pop(source_id, None)
        if self._selected_source_id == source_id:
            self._selected_source_id = None
        self._save()


_registry = _SourceRegistry()


def list_sources() -> list[Source]:
    return _registry.list_sources()


def create_source(request: CreateSourceRequest) -> Source:
    return _registry.create_source(request)


def create_pst_source(request: CreatePstSourceRequest) -> Source:
    return _registry.create_pst_source(request)


def get_source(source_id: str) -> Source | None:
    return _registry.get_source(source_id)


def update_source_path(source_id: str, source_path: str) -> Source:
    return _registry.update_source_path(source_id, source_path)


def select_source(source_id: str) -> Source:
    return _registry.select_source(source_id)


def get_selected_source_id() -> str | None:
    return _registry.get_selected_source_id()

def delete_source(source_id: str) -> None:
    _registry.delete_source(source_id)
