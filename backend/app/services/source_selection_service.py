"""
source_selection_service — In-Memory-Speicherung ausgewählter Tree-Knoten.

Speichert pro source_id eine Liste von selected_node_ids.
Unbekannte source_ids liefern eine leere Auswahl (kein Fehler).
"""


class _SelectionStore:
    def __init__(self) -> None:
        self._selections: dict[str, list[str]] = {}

    def get(self, source_id: str) -> list[str]:
        return list(self._selections.get(source_id, []))

    def set(self, source_id: str, node_ids: list[str]) -> list[str]:
        self._selections[source_id] = list(node_ids)
        return list(self._selections[source_id])

    def clear(self, source_id: str) -> None:
        self._selections.pop(source_id, None)


_store = _SelectionStore()


def get_selection(source_id: str) -> list[str]:
    return _store.get(source_id)


def set_selection(source_id: str, node_ids: list[str]) -> list[str]:
    return _store.set(source_id, node_ids)


def sanitize_selection(source_id: str, valid_node_ids: set[str]) -> list[str]:
    current = _store.get(source_id)
    cleaned = [node_id for node_id in current if node_id in valid_node_ids]
    _store.set(source_id, cleaned)
    return cleaned


def set_validated_selection(source_id: str, node_ids: list[str], valid_node_ids: set[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()

    for node_id in node_ids:
        if node_id not in valid_node_ids:
            continue
        if node_id in seen:
            continue
        seen.add(node_id)
        cleaned.append(node_id)

    _store.set(source_id, cleaned)
    return cleaned
