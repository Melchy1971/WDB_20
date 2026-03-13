export type SourceType = "LOCAL_FOLDER" | "PST";

export type Source = {
  source_id: string;
  source_type: SourceType;
  label: string;
  source_path: string;
  created_at: string;
};

export type CreateSourceRequest = {
  source_type: SourceType;
  label: string;
  source_path: string;
};

export type CreatePstSourceRequest = {
  label: string;
  pst_file_path: string;
};

export type UpdateSourcePathRequest = {
  source_path: string;
};

export type ListSourcesResponse = {
  sources: Source[];
};
