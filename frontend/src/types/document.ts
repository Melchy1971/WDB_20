/** Ein vom Backend gescanntes Dokument — kein Volltext, nur Metadaten + Vorschau. */
export type DocumentScanItem = {
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
};

/** Antwort des Scan-Endpunkts. */
export type DocumentListResponse = {
  items: DocumentScanItem[];
};

/** Anfrage an den Scan-Endpunkt. */
export type FolderSourceRequest = {
  folder_path: string;
};

/** Kommando zum Persistieren — nur die ID, kein Volltext. */
export type PersistDocumentCommand = {
  content_hash: string;
};

/** Antwort des Persistier-Endpunkts. */
export type PersistDocumentResponse = {
  status: "stored" | string;
  file_path: string;
};

export type ApiErrorResponse = {
  detail?: string;
};
