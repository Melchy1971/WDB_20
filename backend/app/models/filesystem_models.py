from pydantic import BaseModel


class FilesystemEntry(BaseModel):
    name: str
    path: str
    is_dir: bool


class FilesystemBrowseResponse(BaseModel):
    current_path: str          # leer = Laufwerksübersicht
    parent_path: str | None    # None = keine übergeordnete Ebene
    entries: list[FilesystemEntry]
