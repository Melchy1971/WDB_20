import type { TreeNodeType } from "./tree";
import type { SourceType } from "./source";

/**
 * Status der Import-Vorschau.
 *
 * "ready" — mindestens ein Knoten ausgewählt, Import wäre möglich
 * "empty" — keine Knoten ausgewählt oder Auswahl enthält keine bekannten Knoten
 */
export type ImportPreviewStatus = "ready" | "empty";

/** Ein einzelner ausgewählter Knoten in der Import-Vorschau. */
export type ImportPreviewItem = {
  node_id: string;
  node_name: string;
  node_type: TreeNodeType;
};

/** GET /sources/{source_id}/import-preview — Response */
export type ImportPreviewResponse = {
  source_id: string;
  source_type: SourceType;
  status: ImportPreviewStatus;
  selected_count: number;
  items: ImportPreviewItem[];
};
