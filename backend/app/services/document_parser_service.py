from email import policy
from email.parser import BytesParser
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentParserService:
	def parse_file(self, file_path: Path) -> tuple[str, str, str, str]:
		extension = file_path.suffix.lower()

		if extension == ".txt":
			text = self._parse_txt(file_path)
			return text, "text/plain", "txt_parser", "parsed"

		if extension == ".pdf":
			text = self._parse_pdf(file_path)
			return text, "application/pdf", "pdf_parser", "parsed"

		if extension == ".docx":
			text = self._parse_docx(file_path)
			return (
				text,
				"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
				"docx_parser",
				"parsed",
			)

		if extension == ".eml":
			text = self._parse_eml(file_path)
			return text, "message/rfc822", "eml_parser", "parsed"

		return "", "application/octet-stream", "unsupported_parser", "unsupported"

	def _parse_txt(self, file_path: Path) -> str:
		return file_path.read_text(encoding="utf-8", errors="ignore")

	def _parse_pdf(self, file_path: Path) -> str:
		reader = PdfReader(str(file_path))
		pages = []

		for page in reader.pages:
			pages.append(page.extract_text() or "")

		return "\n".join(pages).strip()

	def _parse_docx(self, file_path: Path) -> str:
		doc = DocxDocument(str(file_path))
		return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()

	def _parse_eml(self, file_path: Path) -> str:
		with file_path.open("rb") as f:
			msg = BytesParser(policy=policy.default).parse(f)

		subject = msg.get("subject", "")
		sender = msg.get("from", "")
		recipients = msg.get("to", "")
		date = msg.get("date", "")

		body_parts = []

		if msg.is_multipart():
			for part in msg.walk():
				content_type = part.get_content_type()
				disposition = str(part.get("Content-Disposition", ""))

				if "attachment" in disposition.lower():
					continue

				if content_type == "text/plain":
					try:
						body_parts.append(part.get_content())
					except Exception:
						pass
		else:
			try:
				body_parts.append(msg.get_content())
			except Exception:
				pass

		header_block = f"Subject: {subject}\nFrom: {sender}\nTo: {recipients}\nDate: {date}\n"
		body_block = "\n".join(str(part) for part in body_parts)

		return f"{header_block}\n{body_block}".strip()
