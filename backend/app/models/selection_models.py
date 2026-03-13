from pydantic import BaseModel, Field


class SourceSelectionResponse(BaseModel):
    source_id: str
    selected_node_ids: list[str]
    selected_folder_paths: list[str]
    selected_count: int


class UpdateSourceSelectionRequest(BaseModel):
    selected_node_ids: list[str] = Field(default_factory=list)


class UpdateSourceSelectionResponse(BaseModel):
    source_id: str
    selected_node_ids: list[str]
    selected_folder_paths: list[str]
    selected_count: int
