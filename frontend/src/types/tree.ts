/**
 * Repräsentiert einen Knoten im PST-Verzeichnisbaum.
 *
 * node_type:
 *   "folder"     — Ordner (Inbox, Sent, benutzerdefinierte Ordner …)
 *   "message"    — E-Mail-Nachricht (Blatt)
 *   "attachment" — Anhang (Blatt)
 */
export type TreeNodeType = "folder" | "message" | "attachment";

export type TreeNode = {
  id: string;
  name: string;
  node_type: TreeNodeType;
  item_count?: number; // nur bei Ordnern sinnvoll
  children: TreeNode[];
};

/** GET /sources/{source_id}/tree */
export type SourceTreeResponse = {
  source_id: string;
  root: TreeNode;
};
