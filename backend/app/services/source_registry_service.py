from datetime import datetime, timezone
from uuid import uuid4

from app.models.source_models import CreateSourceRequest, Source


class _SourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, Source] = {}

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
        return source

    def get_source(self, source_id: str) -> Source | None:
        return self._sources.get(source_id)


_registry = _SourceRegistry()


def list_sources() -> list[Source]:
    return _registry.list_sources()


def create_source(request: CreateSourceRequest) -> Source:
    return _registry.create_source(request)


def get_source(source_id: str) -> Source | None:
    return _registry.get_source(source_id)
