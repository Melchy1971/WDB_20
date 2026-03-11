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
