import { apiGet, apiPost } from "./client";
import type { Source, CreateSourceRequest } from "../types/source";
import type { DocumentScanResponse, FolderScanRequest } from "../types/document";

export function getSources(): Promise<Source[]> {
  return apiGet<Source[]>("/sources");
}

export function createSource(body: CreateSourceRequest): Promise<Source> {
  return apiPost<CreateSourceRequest, Source>("/sources", body);
}

export function scanFolder(request: FolderScanRequest): Promise<DocumentScanResponse> {
  return apiPost<FolderScanRequest, DocumentScanResponse>("/sources/folder/scan", request);
}
