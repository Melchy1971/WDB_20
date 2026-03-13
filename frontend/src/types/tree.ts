export type TreeNodeType = "folder" | "message" | "attachment";

export type PstFolderNode = {
  id: string;
  name: string;
  path: string;
  parent_path: string | null;
  has_children: boolean;
  message_count: number;
  children: PstFolderNode[];
  node_type: TreeNodeType;
  item_count?: number | null;
};

export type PstTreeResponse = {
  source_id: string | null;
  source_path: string;
  root: PstFolderNode;
};

export type TreeNode = PstFolderNode;
export type SourceTreeResponse = PstTreeResponse;
