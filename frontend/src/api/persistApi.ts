import { apiPost } from "./client";
import type { PersistDocumentCommand, PersistDocumentResponse } from "../types/document";

export function persistDocument(contentHash: string): Promise<PersistDocumentResponse> {
  return apiPost<PersistDocumentCommand, PersistDocumentResponse>("/persist/document", {
    content_hash: contentHash,
  });
}
