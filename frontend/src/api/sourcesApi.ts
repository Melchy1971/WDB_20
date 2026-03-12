import { apiDelete, apiGet, apiPost } from "./client";
import type { DocumentScanResponse } from "../types/document";
import type {
  CreatePstSourceRequest,
  CreateSourceRequest,
  ListSourcesResponse,
  Source,
} from "../types/source";
import type { SourceTreeResponse } from "../types/tree";

export function listSources(): Promise<Source[]> {
  return apiGet<ListSourcesResponse>("/sources").then((res) => res.sources);
}

export function createSource(request: CreateSourceRequest): Promise<Source> {
  return apiPost<CreateSourceRequest, Source>("/sources", request);
}

export function createPstSource(request: CreatePstSourceRequest): Promise<Source> {
  return apiPost<CreatePstSourceRequest, Source>("/sources/pst", request);
}

export function scanSource(sourceId: string): Promise<DocumentScanResponse> {
  return apiPost<object, DocumentScanResponse>(`/sources/${sourceId}/scan`, {});
}

export function fetchSourceTree(sourceId: string): Promise<SourceTreeResponse> {
  return apiGet<SourceTreeResponse>(`/sources/${sourceId}/tree`);
}

export function deleteSource(sourceId: string): Promise<Source> {
  return apiDelete<Source>(`/sources/${sourceId}`);
}
