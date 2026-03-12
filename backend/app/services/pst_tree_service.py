"""
pst_tree_service — Platzhalter für die spätere PST-Baum-Analyse.

Aktueller Stand:
  Gibt eine statische Platzhalter-Struktur zurück, die den API-Vertrag
  für GET /sources/{source_id}/tree erfüllt.
  Keine Datei wird gelesen, kein PST-Parser wird aufgerufen.

Erweiterungspunkt:
  Wenn ein echter PST-Parser (z. B. libpff-python) verfügbar ist,
  ersetzt man den Rumpf von `get_pst_tree()` durch einen echten
  Traversal-Aufruf. Der Endpunkt und die Modelle bleiben unverändert.
"""

from app.models.tree_models import SourceTreeResponse, TreeNode

_PLACEHOLDER_FOLDERS: list[tuple[str, str]] = [
    ("inbox",    "Posteingang"),
    ("sent",     "Gesendete Objekte"),
    ("deleted",  "Gelöschte Elemente"),
    ("calendar", "Kalender"),
    ("contacts", "Kontakte"),
    ("drafts",   "Entwürfe"),
]


def get_pst_tree(source_id: str) -> SourceTreeResponse:
    """
    Gibt eine Platzhalter-Baumstruktur für die angegebene PST-Quelle zurück.

    - Alle Ordner sind leer (item_count=0, children=[]).
    - Keine Nachrichten, keine Anhänge — kein Fake-Inhalt.
    - Struktur entspricht dem Standard-Ordnerlayout einer PST-Datei.
    """
    folders = [
        TreeNode(
            id=folder_id,
            name=label,
            node_type="folder",
            item_count=0,
            children=[],
        )
        for folder_id, label in _PLACEHOLDER_FOLDERS
    ]

    root = TreeNode(
        id="root",
        name="Postfach (Platzhalter)",
        node_type="folder",
        item_count=len(folders),
        children=folders,
    )

    return SourceTreeResponse(source_id=source_id, root=root)
