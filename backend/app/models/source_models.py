from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["LOCAL_FOLDER", "PST"]


class Source(BaseModel):
    source_id: str
    source_type: SourceType
    label: str
    source_path: str  # Ordnerpfad für LOCAL_FOLDER; .pst-Dateipfad für PST
    created_at: str


class CreateSourceRequest(BaseModel):
    """Generisches Request-Modell — verwendet von POST /sources (LOCAL_FOLDER)."""

    source_type: SourceType
    label: str = Field(..., min_length=1)
    source_path: str = Field(..., min_length=1)


class CreatePstSourceRequest(BaseModel):
    """PST-spezifisches Request-Modell — verwendet von POST /sources/pst."""

    label: str = Field(..., min_length=1)
    pst_file_path: str = Field(
        ...,
        min_length=1,
        description="Absoluter Pfad zur .pst-Datei auf dem lokalen Dateisystem",
    )


class UpdateSourcePathRequest(BaseModel):
    source_path: str = Field(..., min_length=1)


class ListSourcesResponse(BaseModel):
    sources: list[Source]


class SelectSourceRequest(BaseModel):
    source_id: str


class SelectSourceResponse(BaseModel):
    selected_source_id: str
    source_type: SourceType


# Verwendet vom Legacy-Endpunkt /sources/folder/scan
class FolderScanRequest(BaseModel):
    folder_path: str = Field(..., min_length=1, description="Absolute or relative local folder path")
