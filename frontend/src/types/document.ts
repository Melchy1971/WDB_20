/** Ein vom Backend gescanntes Dokument — kein Volltext, nur Metadaten + Vorschau. */
export type DocumentScanItem = {
  document_id: string;
  file_name: string;
  file_path: string;
  extension: string;
  mime_type: string;
  source_type: string;
  parser_type: string;
  preview_text: string;
  content_hash: string;
  last_modified: string;
  size_bytes: number;
  parse_status: string;
  parse_error: string | null;
};

/** Antwort des Scan-Endpunkts. */
export type DocumentScanResponse = {
  scan_id: string;
  items: DocumentScanItem[];
};

/** Anfrage an den Scan-Endpunkt. */
export type FolderSourceRequest = {
  folder_path: string;
};

/** Kommando zum Persistieren — nur scan_id + document_id, kein Volltext. */
export type PersistDocumentByIdCommand = {
  scan_id: string;
  document_id: string;
};

/** Antwort des Persistier-Endpunkts. */
export type PersistDocumentResponse = {
  status: "stored" | string;
  file_path: string;
};

export type ApiErrorResponse = {
  detail?: string;
};
