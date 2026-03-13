"""
pst_parser_service - Extrahiert rekursiv die Ordnerstruktur einer PST-Datei.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.adapters.pst_archive_adapter import (
    LibratomPstArchiveAdapter,
    PstCorruptedError,
    PstDependencyMissingError,
    PstError,
)
from app.models.tree_models import SourceTreeResponse, TreeNode
from app.services.pst_access_service import (
    InvalidPstPathError,
    PstAccessDeniedError,
    PstAccessTimeoutError,
    PstFileNotFoundError,
    PstNetworkPathUnavailableError,
    PstParseTimeoutError,
    PstUnreadableError,
    run_pst_parse_with_timeout,
    validate_and_probe_pst_path,
)

logger = logging.getLogger(__name__)


def _normalize_folder_path(parent_path: str | None, node_name: str) -> str:
    if parent_path is None:
        return node_name
    return f"{parent_path}/{node_name}"


def _folder_to_node(
    folder: object,
    adapter: LibratomPstArchiveAdapter,
    parent_path: str | None,
) -> TreeNode:
    node_id = adapter.get_folder_identifier(folder)
    name = adapter.get_folder_name(folder, node_id)
    sub_folders = adapter.get_sub_folders(folder)
    current_path = _normalize_folder_path(parent_path, name)
    children = [_folder_to_node(sub_folder, adapter, current_path) for sub_folder in sub_folders]
    message_count = adapter.get_direct_message_count(folder)

    return TreeNode(
        id=node_id,
        name=name,
        path=current_path,
        parent_path=parent_path,
        has_children=bool(children),
        message_count=message_count,
        children=children,
        node_type="folder",
        item_count=len(children) + message_count,
    )


def _parse_tree_sync(path: Path, source_id: str | None) -> SourceTreeResponse:
    adapter = LibratomPstArchiveAdapter()
    archive = adapter.open_archive(path)
    try:
        root_folder = adapter.get_root_folder(archive)
        root_node = _folder_to_node(root_folder, adapter, parent_path=None)
    finally:
        adapter.close_archive(archive)

    return SourceTreeResponse(source_id=source_id, source_path=str(path), root=root_node)


def parse_pst_tree(pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
    path = validate_and_probe_pst_path(pst_path)
    logger.info("Starte PST-Tree-Parsing", extra={"pst_path": str(path), "source_id": source_id})
    return run_pst_parse_with_timeout(lambda: _parse_tree_sync(path, source_id), path)


class PstParserService:
    @staticmethod
    def build_tree(pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
        return parse_pst_tree(pst_path=pst_path, source_id=source_id)

    @staticmethod
    def collect_valid_node_ids(tree: SourceTreeResponse) -> set[str]:
        return collect_valid_node_ids_from_root(tree.root)


def collect_valid_node_ids_from_root(root: TreeNode) -> set[str]:
    valid_ids: set[str] = set()

    def walk(node: TreeNode) -> None:
        valid_ids.add(node.id)
        for child in node.children:
            walk(child)

    walk(root)
    return valid_ids


__all__ = [
    "InvalidPstPathError",
    "PstAccessDeniedError",
    "PstAccessTimeoutError",
    "PstCorruptedError",
    "PstDependencyMissingError",
    "PstError",
    "PstFileNotFoundError",
    "PstNetworkPathUnavailableError",
    "PstParseTimeoutError",
    "PstParserService",
    "PstUnreadableError",
    "parse_pst_tree",
]
