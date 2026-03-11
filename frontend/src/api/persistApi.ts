import type { ApiErrorResponse, DocumentItem, PersistDocumentResponse } from "../types/document";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function buildErrorMessage(prefix: string, status: number, body: ApiErrorResponse | null): string {
  if (body?.detail) {
    return `${prefix}: ${body.detail}`;
  }

  return `${prefix}: HTTP ${status}`;
}

export async function persistDocument(document: DocumentItem): Promise<PersistDocumentResponse> {
  const response = await fetch(`${API_BASE_URL}/persist/document`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(document),
  });

  if (!response.ok) {
    let errorBody: ApiErrorResponse | null = null;

    try {
      errorBody = (await response.json()) as ApiErrorResponse;
    } catch {
      errorBody = null;
    }

    throw new Error(buildErrorMessage("Persistierung fehlgeschlagen", response.status, errorBody));
  }

  return (await response.json()) as PersistDocumentResponse;
}
