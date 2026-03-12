import { apiGet, apiPost } from "./client";
import type {
  ImportRunAnalysisResponse,
  StartImportRunAnalysisRequest,
  StartImportRunAnalysisResponse,
} from "../types/analysis";

export function startImportRunAnalysis(
  importRunId: string
): Promise<StartImportRunAnalysisResponse> {
  return apiPost<StartImportRunAnalysisRequest, StartImportRunAnalysisResponse>(
    `/import-runs/${importRunId}/analysis`,
    {}
  );
}

export function fetchImportRunAnalysisResults(
  importRunId: string
): Promise<ImportRunAnalysisResponse> {
  return apiGet<ImportRunAnalysisResponse>(`/import-runs/${importRunId}/analysis`);
}
