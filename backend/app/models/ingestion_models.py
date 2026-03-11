from pydantic import BaseModel


class DocumentItem(BaseModel):
	file_name: str
	file_path: str
	extension: str
	mime_type: str
	source_type: str
	parser_type: str
	preview_text: str
	text_content: str
	content_hash: str
	last_modified: str
	size_bytes: int
	parse_status: str


class DocumentListResponse(BaseModel):
	items: list["ParsedDocument"]


class PersistDocumentRequest(BaseModel):
	file_name: str
	file_path: str
	extension: str
	mime_type: str
	source_type: str
	parser_type: str
	preview_text: str
	text_content: str
	content_hash: str
	last_modified: str
	size_bytes: int
	parse_status: str


class PersistDocumentResponse(BaseModel):
	status: str
	file_path: str


class ParsedDocument(BaseModel):
	file_name: str
	file_path: str
	extension: str
	mime_type: str
	source_type: str
	parser_type: str
	preview_text: str
	text_content: str
	content_hash: str
	last_modified: str
	size_bytes: int
	parse_status: str
