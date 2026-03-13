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


class DocumentAnalysisResult(BaseModel):
    document_id: str
    file_name: str
    topic_label: str
    summary: str
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    priority: AnalysisPriority
    confidence: float


class ScanAnalysisResponse(BaseModel):
    scan_id: str
    results: list[DocumentAnalysisResult]


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
