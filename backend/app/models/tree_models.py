from typing import Literal

from pydantic import BaseModel

TreeNodeType = Literal["folder", "message", "attachment"]


class TreeNode(BaseModel):
    """
    Einzelner Knoten im PST-Verzeichnisbaum.

    node_type:
      "folder"     — Ordner (Inbox, Gesendete Objekte, benutzerdefiniert …)
      "message"    — E-Mail-Nachricht (Blattknoten)
      "attachment" — Dateianhang (Blattknoten)

    item_count:
      Anzahl direkter Kindelemente — nur bei Ordnern sinnvoll, sonst None.
    children:
      Leere Liste bei Blattknoten (message, attachment).
    """

    id: str
    name: str
    node_type: TreeNodeType
    item_count: int | None = None
    children: list["TreeNode"] = []


# Pydantic v2: Self-referenzielle Modelle müssen nach der Klassendefinition
# neu gebaut werden, damit der Vorwärts-Verweis in `children` aufgelöst wird.
TreeNode.model_rebuild()


class SourceTreeResponse(BaseModel):
    """GET /sources/{source_id}/tree — Response."""

    source_id: str
    root: TreeNode
