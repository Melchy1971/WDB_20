"""
pst_parser_service — Echter PST-Ordnerbaum-Parser auf Basis von pypff (libpff-python).

Liest die Ordnerhierarchie einer PST/OST-Datei und wandelt sie in
SourceTreeResponse-Modelle um. E-Mail-Inhalte werden *nicht* gelesen.

Voraussetzung:
    pip install libpff-python
    (erfordert Microsoft C++ Build Tools unter Windows)

Raises:
    ImportError   — wenn libpff-python nicht installiert ist
    FileNotFoundError — wenn die PST-Datei nicht existiert
    OSError       — wenn pypff die Datei nicht öffnen kann (beschädigt, kein Zugriff)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import pypff  # type: ignore[import-untyped]
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pypff (libpff-python) ist nicht installiert. "
        "Installiere es mit: pip install libpff-python\n"
        "Unter Windows werden Microsoft C++ Build Tools benötigt: "
        "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    ) from exc

from app.models.tree_models import SourceTreeResponse, TreeNode


def _folder_to_node(folder: Any) -> TreeNode:
    """
    Wandelt einen pypff-Ordner rekursiv in einen TreeNode um.

    node_id:
        Wird aus folder.identifier gebildet (stabiler Integer-Bezeichner
        aus dem PST-Format). Format: Dezimalstring, z. B. "290".
        Damit sind IDs dateiunabhängig reproduzierbar.

    item_count:
        Summe aus Unterordnern + direkten Nachrichten des Ordners.
        Gibt dem Frontend einen schnellen Überblick ohne alle Kinder zu laden.
    """
    node_id = str(folder.identifier)
    name: str = folder.name or f"Ordner-{node_id}"

    children: list[TreeNode] = [
        _folder_to_node(folder.get_sub_folder(i))
        for i in range(folder.number_of_sub_folders)
    ]

    item_count = folder.number_of_sub_folders + folder.number_of_messages

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
        OSError: wenn pypff die Datei nicht lesen kann.
    """
    path = Path(pst_path)
    if not path.exists():
        raise FileNotFoundError(f"PST-Datei nicht gefunden: {pst_path}")
    if not path.is_file():
        raise OSError(f"Pfad ist keine Datei: {pst_path}")

    pff_file: Any = pypff.file()  # type: ignore[attr-defined]
    try:
        pff_file.open(str(path))  # type: ignore[union-attr]
        root_folder: Any = pff_file.get_root_folder()  # type: ignore[union-attr]
        root_node = _folder_to_node(root_folder)
    finally:
        pff_file.close()  # type: ignore[union-attr]

    return SourceTreeResponse(source_id=source_id, root=root_node)
