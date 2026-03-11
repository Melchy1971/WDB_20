export type FolderScanRequest = {
  folder_path: string;
};

export type DocumentItem = {
<<<<<<< HEAD
  file_name: string;
  file_path: string;
  extension: string;
  text_content: string;
  content_hash: string;
  last_modified: string;
  size_bytes: number;
=======
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
>>>>>>> a19e3da ( Changes to be committed:)
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
