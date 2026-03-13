import { apiDelete, apiGet, apiPost } from "./client";
import type { DocumentScanResponse } from "../types/document";
import type {
  CreatePstSourceRequest,
  CreateSourceRequest,
  ListSourcesResponse,
  Source,
  UpdateSourcePathRequest,
} from "../types/source";
import type { PstTreeResponse } from "../types/tree";
import type { ScanAnalysisResponse } from "../types/analysis";

export function listSources(): Promise<Source[]> {
  return apiGet<ListSourcesResponse>("/sources").then((res) => res.sources);
}

export function getSelectedSource(): Promise<{ selected_source_id: string; source_type: string } | null> {
  return apiGet<{ selected_source_id: string; source_type: string } | null>("/sources/selected");
}

export function selectSource(sourceId: string): Promise<{ selected_source_id: string; source_type: string }> {
  return apiPost<{ source_id: string }, { selected_source_id: string; source_type: string }>("/sources/select", {
    source_id: sourceId,
  });
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

export function fetchSourceTree(sourceId: string): Promise<PstTreeResponse> {
  return apiGet<PstTreeResponse>(`/sources/${sourceId}/tree`);
}

export function fetchPstTreeByPath(path: string): Promise<PstTreeResponse> {
  const query = `?path=${encodeURIComponent(path)}`;
  return apiGet<PstTreeResponse>(`/sources/pst/tree${query}`);
}

export function deleteSource(sourceId: string): Promise<Source> {
  return apiDelete<Source>(`/sources/${sourceId}`);
}

export function updateSourcePath(sourceId: string, request: UpdateSourcePathRequest): Promise<Source> {
  return fetch(`${import.meta.env.VITE_API_BASE_URL}/sources/${sourceId}/path`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  }).then(async (res) => {
    if (!res.ok) {
      let detail: string | undefined;
      try {
        const body = (await res.json()) as { detail?: string };
        detail = body.detail;
      } catch {
        // ignore parse errors
      }
      throw new Error(detail ?? `PATCH /sources/${sourceId}/path: HTTP ${res.status}`);
    }
    return res.json() as Promise<Source>;
  });
}

export function analyzeScan(scanId: string): Promise<ScanAnalysisResponse> {
  return apiPost<object, ScanAnalysisResponse>(`/sources/scan-analysis/${scanId}`, {});
}
