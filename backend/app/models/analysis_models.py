from typing import Literal

from pydantic import BaseModel, Field

AnalysisStatus = Literal["queued", "running", "finished", "failed"]
AnalysisPriority = Literal["low", "medium", "high"]


class AnalysisResult(BaseModel):
    topic_label: str
    summary: str
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    priority: AnalysisPriority
    confidence: float


class ImportRunAnalysisRecord(BaseModel):
    import_run_id: str
    status: AnalysisStatus
    results: list[AnalysisResult] = Field(default_factory=list)
    error_message: str | None = None


class StartImportRunAnalysisResponse(BaseModel):
    import_run_id: str
    status: AnalysisStatus
    message: str


class ImportRunAnalysisResponse(BaseModel):
    import_run_id: str
    status: AnalysisStatus
    results: list[AnalysisResult] = Field(default_factory=list)
