import { apiGet } from "./client";
import type { ImportPreviewResponse } from "../types/importPreview";

export function fetchImportPreview(sourceId: string): Promise<ImportPreviewResponse> {
  return apiGet<ImportPreviewResponse>(`/sources/${sourceId}/import-preview`);
}
