export type SourceType = "LOCAL_FOLDER";

/** Eine registrierte Dokumentquelle — vom Backend verwaltet. */
export type Source = {
  source_id: string;
  source_type: SourceType;
  label: string;
  source_path: string; // Ordnerpfad für LOCAL_FOLDER
  created_at: string;
};

/** POST /sources — LOCAL_FOLDER */
export type CreateSourceRequest = {
  source_type: SourceType;
  label: string;
  source_path: string;
};

export type UpdateSourcePathRequest = {
  source_path: string;
};

/** GET /sources — Response */
export type ListSourcesResponse = {
  sources: Source[];
};
