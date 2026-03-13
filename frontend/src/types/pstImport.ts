export type ImportedAttachment = {
  file_name: string;
  mime_type: string | null;
  size_bytes: number | null;
};

export type ImportedEmail = {
  subject: string | null;
  sender: string | null;
  recipients: string[];
  sent_at: string | null;
  body_text: string;
  message_id: string;
  source_folder_path: string;
  attachments: ImportedAttachment[];
};

export type ImportRunStatus = "queued" | "running" | "finished" | "failed";

export type ImportRun = {
  import_run_id: string;
  source_id: string;
  selected_node_ids: string[];
  email_count: number;
  attachment_count: number;
  total_folder_count: number;
  processed_folder_count: number;
  total_message_count_estimate: number;
  processed_message_count: number;
  progress_percent: number | null;
  processed_batches: number;
  failed_batches: number;
  batch_size: number | null;
  error_message: string | null;
  status: ImportRunStatus;
  imported_emails: ImportedEmail[];
};
