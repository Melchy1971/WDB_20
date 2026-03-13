from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import getaddresses
from pathlib import Path
from typing import Any, Protocol, cast
from uuid import uuid4

from app.models.pst_import_models import ImportRun, ImportedAttachment, ImportedEmail
from app.models.tree_models import SourceTreeResponse, TreeNode

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int], None]


class DuplicateMessageRegistry(Protocol):
    def is_duplicate(self, dedup_key: str, email: ImportedEmail, run: ImportRun) -> bool:
        ...


class NoOpDuplicateMessageRegistry:
    def is_duplicate(self, dedup_key: str, email: ImportedEmail, run: ImportRun) -> bool:
        return False


class PstMailExtractor(Protocol):
    def extract_from_run(
        self,
        run: ImportRun,
        progress_callback: ProgressCallback | None = None,
    ) -> list[ImportedEmail]:
        ...


def count_attachments(emails: list[ImportedEmail]) -> int:
    return sum(len(email.attachments) for email in emails)


def calculate_progress_percent(run: ImportRun) -> float | None:
    total_units = run.total_folder_count + run.total_message_count_estimate
    processed_units = run.processed_folder_count + run.processed_message_count

    if total_units <= 0:
        if run.status == "finished":
            return 100.0
        if run.status in {"queued", "running"}:
            return None
        return 0.0

    percent = (processed_units / total_units) * 100
    return round(min(percent, 100.0), 2)


def _load_libratom_archive_type() -> Any:
    try:
        from libratom.lib.pff import PffArchive  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "libratom ist nicht installiert. "
            "Installiere es mit: pip install libratom"
        ) from exc
    return cast(Any, PffArchive)


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _message_body_text(message: object) -> str:
    for attr_name in ("plain_text_body", "rtf_body", "html_body"):
        value = getattr(message, attr_name, None)
        text = _safe_text(value).strip()
        if text:
            return text
    return ""


def _message_recipients(message: object) -> list[str]:
    recipients: list[str] = []
    recipient_objects = getattr(message, "recipients", None)
    if recipient_objects is not None:
        for recipient in recipient_objects:
            email_address = _safe_text(getattr(recipient, "email_address", None)).strip()
            name = _safe_text(getattr(recipient, "name", None)).strip()
            if email_address:
                recipients.append(email_address)
            elif name:
                recipients.append(name)

    if recipients:
        return recipients

    display_to = _safe_text(getattr(message, "display_to", None)).strip()
    if not display_to:
        return []
    parsed = [email for _, email in getaddresses([display_to]) if email]
    return parsed or [display_to]


def _message_sender(message: object) -> str | None:
    for attr_name in ("sender_email_address", "sender_name", "sender"):
        value = _safe_text(getattr(message, attr_name, None)).strip()
        if value:
            return value
    return None


def _message_sent_at(message: object) -> datetime | None:
    for attr_name in ("client_submit_time", "delivery_time", "creation_time"):
        value = getattr(message, attr_name, None)
        if isinstance(value, datetime):
            return value
    return None


def _message_id(message: object) -> str:
    transport_headers = _safe_text(getattr(message, "transport_headers", None))
    for line in transport_headers.splitlines():
        if line.lower().startswith("message-id:"):
            message_id = line.split(":", 1)[1].strip()
            if message_id:
                return message_id

    for attr_name in ("internet_message_identifier", "identifier"):
        value = _safe_text(getattr(message, attr_name, None)).strip()
        if value:
            return value

    return ""


def _message_attachments(message: object) -> list[ImportedAttachment]:
    attachments: list[ImportedAttachment] = []
    attachment_objects = getattr(message, "attachments", None)
    if attachment_objects is None:
        return attachments

    for attachment in attachment_objects:
        file_name = (
            _safe_text(getattr(attachment, "name", None)).strip()
            or _safe_text(getattr(attachment, "long_filename", None)).strip()
            or _safe_text(getattr(attachment, "filename", None)).strip()
            or _safe_text(getattr(attachment, "identifier", None)).strip()
        )
        if not file_name:
            continue
        mime_type = _safe_text(getattr(attachment, "mime_type", None)).strip() or None
        size_bytes_value = getattr(attachment, "size", None)
        if not isinstance(size_bytes_value, int):
            size_bytes_value = getattr(attachment, "data_size", None)
        size_bytes = size_bytes_value if isinstance(size_bytes_value, int) else None

        attachments.append(
            ImportedAttachment(
                file_name=file_name,
                mime_type=mime_type,
                size_bytes=size_bytes,
            )
        )

    return attachments


def _iter_folders_with_paths(root_folder: Any):
    stack: list[tuple[object, str]] = [(root_folder, _safe_text(getattr(root_folder, "name", None)) or "root")]

    while stack:
        folder, folder_path = stack.pop()
        yield folder, folder_path

        sub_folders = getattr(folder, "sub_folders", None)
        if sub_folders is None:
            number_of_sub_folders = getattr(folder, "number_of_sub_folders", None)
            get_sub_folder = getattr(folder, "get_sub_folder", None)
            if isinstance(number_of_sub_folders, int) and callable(get_sub_folder):
                sub_folders = [get_sub_folder(i) for i in range(number_of_sub_folders)]
            else:
                sub_folders = []

        for sub_folder in reversed(list(sub_folders)):
            sub_name = _safe_text(getattr(sub_folder, "name", None)) or "unnamed-folder"
            stack.append((sub_folder, f"{folder_path}/{sub_name}"))


def _normalize_for_hash(value: str | None) -> str:
    return (value or "").strip().lower()


def build_dedup_key(email: ImportedEmail) -> str:
    if email.message_id.strip():
        return f"message-id:{email.message_id.strip().lower()}"

    sent_at = email.sent_at.isoformat() if email.sent_at is not None else ""
    body_excerpt = _normalize_for_hash(email.body_text)[:512]
    raw = "||".join(
        [
            _normalize_for_hash(email.subject),
            _normalize_for_hash(email.sender),
            sent_at,
            body_excerpt,
        ]
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"fallback:{digest}"


class LibratomPstMailExtractor:
    def __init__(self, duplicate_registry: DuplicateMessageRegistry | None = None) -> None:
        self._duplicate_registry = duplicate_registry or NoOpDuplicateMessageRegistry()

    def extract_from_run(
        self,
        run: ImportRun,
        progress_callback: ProgressCallback | None = None,
    ) -> list[ImportedEmail]:
        archive_type: Any = _load_libratom_archive_type()
        archive: Any = archive_type()
        archive.load(str(Path(run.source_path)))

        try:
            data_obj: Any = getattr(archive, "_data", None)
            root_folder: Any = getattr(data_obj, "root_folder", None)
            if root_folder is None:
                folders_method: Any = getattr(archive, "folders", None)
                if callable(folders_method):
                    folder_iter: Any = folders_method()
                    root_folder = next(folder_iter)
            if root_folder is None:
                raise OSError("Root-Ordner für PST-Extraktion konnte nicht ermittelt werden.")

            selected_ids = set(run.selected_node_ids)
            dedup_keys_seen: set[str] = set()
            emails: list[ImportedEmail] = []
            processed_folder_count = 0
            processed_message_count = 0
            duplicate_count = 0

            for folder, folder_path in _iter_folders_with_paths(root_folder):
                folder_id = _safe_text(getattr(folder, "identifier", None))
                if folder_id not in selected_ids:
                    continue

                sub_messages = getattr(folder, "sub_messages", None)
                if sub_messages is None:
                    number_of_sub_messages = getattr(folder, "number_of_sub_messages", 0)
                    get_sub_message = getattr(folder, "get_sub_message", None)
                    if isinstance(number_of_sub_messages, int) and callable(get_sub_message):
                        sub_messages = [get_sub_message(i) for i in range(number_of_sub_messages)]
                    else:
                        sub_messages = []

                for message in sub_messages:
                    email = ImportedEmail(
                        subject=_safe_text(getattr(message, "subject", None)).strip() or None,
                        sender=_message_sender(message),
                        recipients=_message_recipients(message),
                        sent_at=_message_sent_at(message),
                        body_text=_message_body_text(message),
                        message_id=_message_id(message),
                        source_folder_path=folder_path,
                        attachments=_message_attachments(message),
                    )
                    processed_message_count += 1
                    dedup_key = build_dedup_key(email)

                    if dedup_key in dedup_keys_seen or self._duplicate_registry.is_duplicate(dedup_key, email, run):
                        duplicate_count += 1
                        logger.info(
                            "PST-Dublette verworfen",
                            extra={
                                "import_run_id": run.import_run_id,
                                "dedup_key": dedup_key,
                                "message_id": email.message_id,
                                "source_folder_path": email.source_folder_path,
                            },
                        )
                    else:
                        dedup_keys_seen.add(dedup_key)
                        emails.append(email)

                    if progress_callback is not None:
                        progress_callback(processed_folder_count, processed_message_count)

                processed_folder_count += 1
                if progress_callback is not None:
                    progress_callback(processed_folder_count, processed_message_count)

            run.duplicate_count = duplicate_count
            return emails
        finally:
            close_method: Any = getattr(archive, "close", None)
            if callable(close_method):
                close_method()
            else:
                data_obj: Any = getattr(archive, "_data", None)
                data_close: Any = getattr(data_obj, "close", None)
                if callable(data_close):
                    data_close()


def collect_valid_node_ids(tree: SourceTreeResponse) -> set[str]:
    valid_ids: set[str] = set()

    def walk(node: TreeNode) -> None:
        valid_ids.add(node.id)
        for child in node.children:
            walk(child)

    walk(tree.root)
    return valid_ids


def build_folder_path_index(tree: SourceTreeResponse) -> dict[str, str]:
    index: dict[str, str] = {}

    def walk(node: TreeNode) -> None:
        index[node.id] = node.path
        for child in node.children:
            walk(child)

    walk(tree.root)
    return index


def build_message_count_estimate_index(tree: SourceTreeResponse) -> dict[str, int]:
    index: dict[str, int] = {}

    def walk(node: TreeNode) -> None:
        index[node.id] = node.message_count
        for child in node.children:
            walk(child)

    walk(tree.root)
    return index


def build_import_run(
    source_id: str,
    source_path: str,
    selected_node_ids: list[str],
    tree: SourceTreeResponse,
) -> ImportRun:
    folder_path_index = build_folder_path_index(tree)
    message_count_index = build_message_count_estimate_index(tree)
    valid_ids = collect_valid_node_ids(tree)

    normalized_selected_ids: list[str] = []
    seen: set[str] = set()
    for node_id in selected_node_ids:
        if node_id not in valid_ids:
            continue
        if node_id in seen:
            continue
        seen.add(node_id)
        normalized_selected_ids.append(node_id)

    selected_folder_paths = [
        folder_path_index[node_id]
        for node_id in normalized_selected_ids
        if node_id in folder_path_index
    ]
    total_message_count_estimate = sum(message_count_index.get(node_id, 0) for node_id in normalized_selected_ids)

    run = ImportRun(
        import_run_id=str(uuid4()),
        source_id=source_id,
        source_path=source_path,
        selected_node_ids=normalized_selected_ids,
        selected_folder_paths=selected_folder_paths,
        status="queued",
        started_at=datetime.now(timezone.utc),
        total_folder_count=len(normalized_selected_ids),
        processed_folder_count=0,
        total_message_count_estimate=total_message_count_estimate,
        processed_message_count=0,
        imported_count=0,
        duplicate_count=0,
    )
    run.progress_percent = calculate_progress_percent(run)
    return run
