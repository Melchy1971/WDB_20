import { apiPost } from "./client";
import type { DocumentItem, PersistDocumentResponse } from "../types/document";

export function persistDocument(document: DocumentItem): Promise<PersistDocumentResponse> {
  return apiPost<DocumentItem, PersistDocumentResponse>("/persist/document", document);
}
