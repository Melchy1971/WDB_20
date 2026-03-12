"""
import_preview_service — Preview der ausgewählten Tree-Knoten für den späteren PST-Import.

Aktueller Stand:
  Kombiniert Source, gespeicherte Selektion und PST-Tree-Struktur zu einer
  Import-Vorschau. Kein echter Import, kein PST-Parser-Aufruf, keine Maildaten.

Erweiterungspunkt:
  Wenn echter PST-Import implementiert wird, nimmt dieser Service die
  Knotenliste entgegen und übergibt sie an den Import-Service.
  `get_import_preview()` selbst bleibt unverändert.
"""

from app.models.import_models import ImportPreviewItem, ImportPreviewResponse
from app.models.source_models import Source
from app.models.tree_models import TreeNode


def _collect_selected_nodes(
    node: TreeNode, id_set: set[str]
) -> list[ImportPreviewItem]:
    """Traversiert den Baum rekursiv und sammelt alle Knoten, deren id in id_set liegt."""
    result: list[ImportPreviewItem] = []
    if node.id in id_set:
        result.append(
            ImportPreviewItem(
                node_id=node.id,
                node_name=node.name,
                node_type=node.node_type,
            )
        )
    for child in node.children:
        result.extend(_collect_selected_nodes(child, id_set))
    return result


def get_import_preview(
    source: Source,
    selected_node_ids: list[str],
    tree_root: TreeNode,
) -> ImportPreviewResponse:
    """
    Gibt eine Vorschau der ausgewählten Knoten zurück.

    - Liest keine PST-Datei.
    - Erzeugt keine Nachrichten oder Anhänge.
    - Kreuzt nur selected_node_ids gegen den bekannten Tree ab.
    """
    if not selected_node_ids:
        return ImportPreviewResponse(
            source_id=source.source_id,
            source_type=source.source_type,
            status="empty",
            selected_count=0,
            items=[],
        )

    id_set = set(selected_node_ids)
    items = _collect_selected_nodes(tree_root, id_set)

    return ImportPreviewResponse(
        source_id=source.source_id,
        source_type=source.source_type,
        status="ready" if items else "empty",
        selected_count=len(items),
        items=items,
    )
