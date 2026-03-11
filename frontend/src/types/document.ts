export type FolderScanRequest = {
  folder_path: string;
};

export type DocumentItem = {
  file_name: string;
  file_path: string;
  extension: string;
  mime_type: string;
  source_type: string;
  parser_type: string;
  preview_text: string;
  text_content: string;
  content_hash: string;
  last_modified: string;
  size_bytes: number;
  parse_status: string;
};

export type DocumentScanResponse = {
  items: DocumentItem[];
};

export type PersistDocumentResponse = {
  status: "stored" | string;
  file_path: string;
};

export type ApiErrorResponse = {
  detail?: string;
};

export type SourceType = "folder" | "pst" | "imap";

export type Source = {
  id: string;
  name: string;
  type: SourceType;
  path: string;
  created_at: string;
};

export type CreateSourceRequest = {
  name: string;
  type: SourceType;
  path: string;
};

export type Topic = {
  id: string;
  label: string;
  description: string;
  document_count: number;
  status: "pending" | "reviewed" | "rejected";
};

export type TopicReviewRequest = {
  topic_id: string;
  action: "approve" | "reject";
};

export type Page = "status" | "sources" | "scan" | "topics";

export type NavItem = {
  page: Page;
  label: string;
};

export const NAV_ITEMS: NavItem[] = [
  { page: "status", label: "System Status" },
  { page: "sources", label: "Quellen" },
  { page: "scan", label: "Ordnerscan" },
  { page: "topics", label: "Themen prüfen" },
];
