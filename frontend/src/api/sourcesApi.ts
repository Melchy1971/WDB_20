import { apiGet, apiPost } from "./client";
import type { DocumentScanResponse } from "../types/document";
import type { CreateSourceRequest, ListSourcesResponse, Source } from "../types/source";

export function listSources(): Promise<Source[]> {
  return apiGet<ListSourcesResponse>("/sources").then((res) => res.sources);
}

export function createSource(request: CreateSourceRequest): Promise<Source> {
  return apiPost<CreateSourceRequest, Source>("/sources", request);
}

export function scanSource(sourceId: string): Promise<DocumentScanResponse> {
  return apiPost<object, DocumentScanResponse>(`/sources/${sourceId}/scan`, {});
}
