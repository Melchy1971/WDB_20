export type SourceSelection = {
  source_id: string;
  selected_node_ids: string[];
  selected_folder_paths: string[];
  selected_count: number;
};

export type UpdateSourceSelectionRequest = {
  selected_node_ids: string[];
};

export type UpdateSourceSelectionResponse = {
  source_id: string;
  selected_node_ids: string[];
  selected_folder_paths: string[];
  selected_count: number;
};
