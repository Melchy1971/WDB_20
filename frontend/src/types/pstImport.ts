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
  error_message: string | null;
  status: ImportRunStatus;
  imported_emails: ImportedEmail[];
};
