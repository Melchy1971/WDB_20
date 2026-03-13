from __future__ import annotations

from dataclasses import dataclass

from app.models.tree_models import SourceTreeResponse, TreeNode


@dataclass
class SourceSelectionRecord:
    selected_node_ids: list[str]
    selected_folder_paths: list[str]


class _SelectionStore:
    def __init__(self) -> None:
        self._selections: dict[str, SourceSelectionRecord] = {}

    def get(self, source_id: str) -> SourceSelectionRecord:
        record = self._selections.get(source_id)
        if record is None:
            return SourceSelectionRecord(selected_node_ids=[], selected_folder_paths=[])
        return SourceSelectionRecord(
            selected_node_ids=list(record.selected_node_ids),
            selected_folder_paths=list(record.selected_folder_paths),
        )

    def set(self, source_id: str, record: SourceSelectionRecord) -> SourceSelectionRecord:
        stored = SourceSelectionRecord(
            selected_node_ids=list(record.selected_node_ids),
            selected_folder_paths=list(record.selected_folder_paths),
        )
        self._selections[source_id] = stored
        return self.get(source_id)

    def clear(self, source_id: str) -> None:
        self._selections.pop(source_id, None)


_store = _SelectionStore()


def _build_folder_path_index(tree: SourceTreeResponse) -> dict[str, str]:
    index: dict[str, str] = {}

    def walk(node: TreeNode) -> None:
        index[node.id] = node.path
        for child in node.children:
            walk(child)

    walk(tree.root)
    return index


def _normalize_node_ids(node_ids: list[str], valid_node_ids: set[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()

    for node_id in node_ids:
        if node_id not in valid_node_ids or node_id in seen:
            continue
        seen.add(node_id)
        cleaned.append(node_id)

    return cleaned


def _record_for_tree(node_ids: list[str], tree: SourceTreeResponse) -> SourceSelectionRecord:
    folder_path_index = _build_folder_path_index(tree)
    valid_node_ids = set(folder_path_index.keys())
    normalized_node_ids = _normalize_node_ids(node_ids, valid_node_ids)
    selected_folder_paths = [folder_path_index[node_id] for node_id in normalized_node_ids]
    return SourceSelectionRecord(
        selected_node_ids=normalized_node_ids,
        selected_folder_paths=selected_folder_paths,
    )


def get_selection_record(source_id: str) -> SourceSelectionRecord:
    return _store.get(source_id)


def get_selection(source_id: str) -> list[str]:
    return get_selection_record(source_id).selected_node_ids


def set_selection(source_id: str, node_ids: list[str]) -> list[str]:
    record = SourceSelectionRecord(selected_node_ids=list(node_ids), selected_folder_paths=[])
    return _store.set(source_id, record).selected_node_ids


def set_selection_for_tree(
    source_id: str,
    node_ids: list[str],
    tree: SourceTreeResponse,
) -> SourceSelectionRecord:
    record = _record_for_tree(node_ids, tree)
    return _store.set(source_id, record)


def sanitize_selection(source_id: str, valid_node_ids: set[str]) -> list[str]:
    current = _store.get(source_id)
    cleaned = _normalize_node_ids(current.selected_node_ids, valid_node_ids)
    stored = SourceSelectionRecord(
        selected_node_ids=cleaned,
        selected_folder_paths=[
            path for node_id, path in zip(current.selected_node_ids, current.selected_folder_paths, strict=False)
            if node_id in valid_node_ids
        ],
    )
    _store.set(source_id, stored)
    return cleaned


def sanitize_selection_for_tree(source_id: str, tree: SourceTreeResponse) -> SourceSelectionRecord:
    current = _store.get(source_id)
    return _store.set(source_id, _record_for_tree(current.selected_node_ids, tree))


def set_validated_selection(source_id: str, node_ids: list[str], valid_node_ids: set[str]) -> list[str]:
    cleaned = _normalize_node_ids(node_ids, valid_node_ids)
    record = SourceSelectionRecord(selected_node_ids=cleaned, selected_folder_paths=[])
    return _store.set(source_id, record).selected_node_ids
