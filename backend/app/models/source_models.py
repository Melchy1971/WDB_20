from pydantic import BaseModel, Field


class FolderScanRequest(BaseModel):
    folder_path: str = Field(..., min_length=1, description="Absolute or relative local folder path")
