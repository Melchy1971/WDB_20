from typing import Literal

from pydantic import BaseModel

from app.models.source_models import SourceType
from app.models.tree_models import TreeNodeType

ImportPreviewStatus = Literal["ready", "empty"]


class ImportPreviewItem(BaseModel):
    """
    Ein einzelner ausgewählter Tree-Knoten in der Import-Vorschau.

    Enthält ausschließlich Strukturinformationen — keine Nachrichteninhalte,
    keine Anhänge, keine Metadaten aus der PST-Datei.
    """

    node_id: str
    node_name: str
    node_type: TreeNodeType


class ImportPreviewResponse(BaseModel):
    """GET /sources/{source_id}/import-preview — Response.

    status:
      "ready" — mindestens ein Knoten ausgewählt, Import wäre möglich
      "empty" — keine Knoten ausgewählt, Import wäre leer
    """

    source_id: str
    source_type: SourceType
    status: ImportPreviewStatus
    selected_count: int
    items: list[ImportPreviewItem]
