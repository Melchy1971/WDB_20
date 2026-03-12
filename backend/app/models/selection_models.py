from pydantic import BaseModel


class SourceSelectionResponse(BaseModel):
    """GET /sources/{source_id}/selection — Response."""

    source_id: str
    selected_node_ids: list[str]


class UpdateSourceSelectionRequest(BaseModel):
    """POST /sources/{source_id}/selection — Request-Body."""

    selected_node_ids: list[str]


class UpdateSourceSelectionResponse(BaseModel):
    """POST /sources/{source_id}/selection — Response."""

    source_id: str
    selected_node_ids: list[str]
