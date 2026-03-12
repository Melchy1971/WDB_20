/** GET /sources/{source_id}/selection — Response */
export type SourceSelection = {
  source_id: string;
  selected_node_ids: string[];
};

/** POST /sources/{source_id}/selection — Request-Body */
export type UpdateSourceSelectionRequest = {
  selected_node_ids: string[];
};

/** POST /sources/{source_id}/selection — Response */
export type UpdateSourceSelectionResponse = {
  source_id: string;
  selected_node_ids: string[];
};
