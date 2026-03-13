from typing import Literal

from pydantic import BaseModel, Field

TreeNodeType = Literal["folder", "message", "attachment"]


class TreeNode(BaseModel):
    id: str
    name: str
    path: str
    parent_path: str | None = None
    has_children: bool
    message_count: int = 0
    children: list["TreeNode"] = Field(default_factory=list)
    node_type: TreeNodeType = "folder"
    item_count: int | None = None


TreeNode.model_rebuild()


class SourceTreeResponse(BaseModel):
    source_id: str | None = None
    source_path: str
    root: TreeNode


class PstTreeRequest(BaseModel):
    path: str = Field(..., min_length=1, description="Absoluter Pfad zur PST-Datei")
