import { apiGet, apiPost } from "./client";
import type { ImportJobStatusResponse, StartImportJobResponse } from "../types/job";

/** POST /sources/{source_id}/import-jobs — startet einen neuen Import-Job */
export function startImportJob(sourceId: string): Promise<StartImportJobResponse> {
  return apiPost<Record<string, never>, StartImportJobResponse>(
    `/sources/${sourceId}/import-jobs`,
    {}
  );
}

/** GET /import-jobs/{job_id} — aktuellen Status eines Jobs abrufen */
export function fetchImportJobStatus(jobId: string): Promise<ImportJobStatusResponse> {
  return apiGet<ImportJobStatusResponse>(`/import-jobs/${jobId}`);
}
