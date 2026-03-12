import { apiPost } from "./client";
import type { PersistDocumentByIdCommand, PersistDocumentResponse } from "../types/document";

export function persistDocument(scanId: string, documentId: string): Promise<PersistDocumentResponse> {
  return apiPost<PersistDocumentByIdCommand, PersistDocumentResponse>("/persist/document", {
    scan_id: scanId,
    document_id: documentId,
  });
}
