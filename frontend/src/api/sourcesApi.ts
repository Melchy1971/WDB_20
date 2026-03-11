import { apiPost } from "./client";
import type { DocumentListResponse, FolderSourceRequest } from "../types/document";

export function scanFolder(request: FolderSourceRequest): Promise<DocumentListResponse> {
  return apiPost<FolderSourceRequest, DocumentListResponse>("/sources/folder/scan", request);
}
