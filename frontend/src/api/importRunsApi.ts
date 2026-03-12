import { apiGet } from "./client";
import type { ImportRun } from "../types/pstImport";

export function fetchImportRun(importRunId: string): Promise<ImportRun> {
  return apiGet<ImportRun>(`/import-runs/${importRunId}`);
}
