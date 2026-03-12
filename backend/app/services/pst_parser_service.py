"""
pst_parser_service — Echter PST-Ordnerbaum-Parser auf Basis von libratom.

Liest die Ordnerhierarchie einer PST/OST-Datei und wandelt sie in
SourceTreeResponse-Modelle um. E-Mail-Inhalte werden *nicht* gelesen.

Hinweis:
    libratom selbst kapselt intern pff-Handling. Die lokale API kann je nach
    Version variieren; daher nutzt dieser Service eine kleine Adapter-Schicht.

Raises:
    ImportError      — wenn libratom nicht installiert ist
    FileNotFoundError — wenn die PST-Datei nicht existiert
    OSError          — wenn die Datei nicht gelesen werden kann
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.tree_models import SourceTreeResponse, TreeNode


def _load_libratom_archive_type() -> Any:
    try:
        from libratom.lib.pff import PffArchive  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "libratom ist nicht installiert. "
            "Installiere es mit: pip install libratom"
        ) from exc
    return PffArchive


class _LibratomPstAdapter:
    """Adapter für unterschiedliche libratom/pff-Objektformen."""

    @staticmethod
    def open_archive(pst_path: Path) -> Any:
        archive_type = _load_libratom_archive_type()
        archive = archive_type()
        if hasattr(archive, "load"):
            archive.load(str(pst_path))
            return archive
        raise OSError("libratom PffArchive unterstützt keine load()-Methode.")

    @staticmethod
    def close_archive(archive: Any) -> None:
        close_method = getattr(archive, "close", None)
        if callable(close_method):
            close_method()
            return
        data_obj = getattr(archive, "_data", None)
        data_close = getattr(data_obj, "close", None)
        if callable(data_close):
            data_close()

    @staticmethod
    def get_root_folder(archive: Any) -> Any:
        data_obj = getattr(archive, "_data", None)
        root_folder = getattr(data_obj, "root_folder", None)
        if root_folder is not None:
            return root_folder

        folders_method = getattr(archive, "folders", None)
        if callable(folders_method):
            folder_iter = folders_method()
            try:
                return next(folder_iter)
            except StopIteration as exc:
                raise OSError("PST enthält keine Root-Ordnerstruktur.") from exc

        raise OSError("Root-Ordner konnte über libratom nicht ermittelt werden.")

    @staticmethod
    def get_folder_identifier(folder: Any) -> str:
        identifier = getattr(folder, "identifier", None)
        if identifier is None:
            raise OSError("Ordner-Identifier fehlt; stabile node_id kann nicht gebildet werden.")
        return str(identifier)

    @staticmethod
    def get_folder_name(folder: Any, node_id: str) -> str:
        name = getattr(folder, "name", None)
        return name or f"Ordner-{node_id}"

    @staticmethod
    def get_sub_folders(folder: Any) -> list[Any]:
        sub_folders = getattr(folder, "sub_folders", None)
        if sub_folders is not None:
            return list(sub_folders)

        number_of_sub_folders = getattr(folder, "number_of_sub_folders", None)
        get_sub_folder = getattr(folder, "get_sub_folder", None)
        if isinstance(number_of_sub_folders, int) and callable(get_sub_folder):
            return [get_sub_folder(i) for i in range(number_of_sub_folders)]

        return []

    @staticmethod
    def get_direct_message_count(folder: Any) -> int:
        for attr_name in ("number_of_sub_messages", "number_of_messages"):
            value = getattr(folder, attr_name, None)
            if isinstance(value, int):
                return value
        return 0


def _folder_to_node(folder: Any, adapter: _LibratomPstAdapter) -> TreeNode:
    """
    Wandelt einen PST-Ordner rekursiv in einen TreeNode um.

    node_id:
        Wird aus folder.identifier gebildet (stabiler Integer-Bezeichner
        aus dem PST-Format). Format: Dezimalstring, z. B. "290".

    item_count:
        Summe aus Unterordnern + direkten Nachrichten des Ordners.
    """
    node_id = adapter.get_folder_identifier(folder)
    name = adapter.get_folder_name(folder, node_id)
    sub_folders = adapter.get_sub_folders(folder)

    children = [_folder_to_node(sub_folder, adapter) for sub_folder in sub_folders]
    item_count = len(sub_folders) + adapter.get_direct_message_count(folder)

    return TreeNode(
        id=node_id,
        name=name,
        node_type="folder",
        item_count=item_count,
        children=children,
    )


def parse_pst_tree(pst_path: str, source_id: str) -> SourceTreeResponse:
    """
    Öffnet die PST-Datei unter *pst_path* und gibt die vollständige
    Ordnerstruktur als SourceTreeResponse zurück.

    Nur Ordner werden traversiert — Nachrichten und Anhänge werden
    *nicht* geladen (kein E-Mail-Inhalt). item_count enthält jedoch
    die Anzahl direkter Nachrichten je Ordner als numerischen Hinweis.

    Args:
        pst_path:  Absoluter Dateisystempfad zur .pst/.ost-Datei.
        source_id: UUID der zugehörigen Source (wird 1:1 weitergereicht).

    Returns:
        SourceTreeResponse mit der vollständigen Ordnerhierarchie.

    Raises:
        FileNotFoundError: wenn *pst_path* nicht auf dem Dateisystem existiert.
        OSError: wenn libratom die Datei nicht lesen kann.
    """
    path = Path(pst_path)
    if not path.exists():
        raise FileNotFoundError(f"PST-Datei nicht gefunden: {pst_path}")
    if not path.is_file():
        raise OSError(f"Pfad ist keine Datei: {pst_path}")

    adapter = _LibratomPstAdapter()
    archive = adapter.open_archive(path)
    try:
        root_folder = adapter.get_root_folder(archive)
        root_node = _folder_to_node(root_folder, adapter)
    finally:
        adapter.close_archive(archive)

    return SourceTreeResponse(source_id=source_id, root=root_node)


class PstParserService:
    @staticmethod
    def build_tree(source_id: str, pst_path: str) -> SourceTreeResponse:
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
