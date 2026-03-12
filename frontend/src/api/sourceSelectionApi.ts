import { apiGet, apiPost } from "./client";
import type {
  SourceSelection,
  UpdateSourceSelectionRequest,
  UpdateSourceSelectionResponse,
} from "../types/selection";

export function fetchSelection(sourceId: string): Promise<SourceSelection> {
  return apiGet<SourceSelection>(`/sources/${sourceId}/selection`);
}

export function saveSelection(
  sourceId: string,
  selectedNodeIds: string[]
): Promise<UpdateSourceSelectionResponse> {
  return apiPost<UpdateSourceSelectionRequest, UpdateSourceSelectionResponse>(
    `/sources/${sourceId}/selection`,
    { selected_node_ids: selectedNodeIds }
  );
}
