export type SourceType = "LOCAL_FOLDER" | "PST";

/** Eine registrierte Dokumentquelle — vom Backend verwaltet. */
export type Source = {
  source_id: string;
  source_type: SourceType;
  label: string;
  source_path: string; // Ordnerpfad für LOCAL_FOLDER; .pst-Dateipfad für PST
  created_at: string;
};

/** POST /sources — LOCAL_FOLDER */
export type CreateSourceRequest = {
  source_type: SourceType;
  label: string;
  source_path: string;
};

/** POST /sources/pst — PST */
export type CreatePstSourceRequest = {
  label: string;
  pst_file_path: string;
};

/** GET /sources — Response */
export type ListSourcesResponse = {
  sources: Source[];
};
