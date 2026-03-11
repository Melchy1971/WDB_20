import type { ApiErrorResponse, DocumentScanResponse, FolderScanRequest } from "../types/document";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function buildErrorMessage(prefix: string, status: number, body: ApiErrorResponse | null): string {
  if (body?.detail) {
    return `${prefix}: ${body.detail}`;
  }

  return `${prefix}: HTTP ${status}`;
}

export async function scanFolder(request: FolderScanRequest): Promise<DocumentScanResponse> {
  const response = await fetch(`${API_BASE_URL}/sources/folder/scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorBody: ApiErrorResponse | null = null;

    try {
      errorBody = (await response.json()) as ApiErrorResponse;
    } catch {
      errorBody = null;
    }

    throw new Error(buildErrorMessage("Ordnerscan fehlgeschlagen", response.status, errorBody));
  }

  return (await response.json()) as DocumentScanResponse;
}
