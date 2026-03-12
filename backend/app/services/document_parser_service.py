from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


@dataclass
class ParseResult:
	text_content: str
	mime_type: str
	parser_type: str
	parse_status: str           # "parsed" | "failed" | "unsupported"
	parse_error: str | None = field(default=None)


class DocumentParserService:
	def parse_file(self, file_path: Path) -> ParseResult:
		"""
		Parst eine Datei und gibt immer ein ParseResult zurück.
		Exceptions der Format-Parser werden pro Datei isoliert — kein globaler Abbruch.
		"""
		extension = file_path.suffix.lower()

		if extension == ".txt":
			return self._safe_parse(
				self._parse_txt, file_path,
				mime_type="text/plain",
				parser_type="txt_parser",
			)

		if extension == ".pdf":
			return self._safe_parse(
				self._parse_pdf, file_path,
				mime_type="application/pdf",
				parser_type="pdf_parser",
			)

		if extension == ".docx":
			return self._safe_parse(
				self._parse_docx, file_path,
				mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
				parser_type="docx_parser",
			)

		if extension == ".eml":
			return self._safe_parse(
				self._parse_eml, file_path,
				mime_type="message/rfc822",
				parser_type="eml_parser",
			)

		return ParseResult(
			text_content="",
			mime_type="application/octet-stream",
			parser_type="unsupported_parser",
			parse_status="unsupported",
		)

	# ── Interner Wrapper ───────────────────────────────────────────────────────

	def _safe_parse(
		self,
		parser_fn,
		file_path: Path,
		*,
		mime_type: str,
		parser_type: str,
	) -> ParseResult:
		try:
			text_content = parser_fn(file_path)
			return ParseResult(
				text_content=text_content,
				mime_type=mime_type,
				parser_type=parser_type,
				parse_status="parsed",
			)
		except Exception as exc:
			return ParseResult(
				text_content="",
				mime_type=mime_type,
				parser_type=parser_type,
				parse_status="failed",
				parse_error=f"{type(exc).__name__}: {exc}",
			)

	# ── Format-Parser ──────────────────────────────────────────────────────────

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
