from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["LOCAL_FOLDER", "PST"]


class Source(BaseModel):
    source_id: str
    source_type: SourceType
    label: str
    source_path: str  # folder path for LOCAL_FOLDER; .pst file path for PST
    created_at: str


class CreateSourceRequest(BaseModel):
    source_type: SourceType
    label: str = Field(..., min_length=1)
    source_path: str = Field(..., min_length=1)


class ListSourcesResponse(BaseModel):
    sources: list[Source]


# Used by the legacy /sources/folder/scan endpoint
class FolderScanRequest(BaseModel):
    folder_path: str = Field(..., min_length=1, description="Absolute or relative local folder path")
