from app.models.document_models import Document

_store: dict[str, Document] = {}


def put(document: Document) -> None:
    _store[document.content_hash] = document


def get(content_hash: str) -> Document | None:
    return _store.get(content_hash)


def clear() -> None:
    _store.clear()
