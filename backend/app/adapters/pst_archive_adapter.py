from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PstError(Exception):
    code = "PST_ERROR"
    status_code = 422

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def to_client_detail(self) -> str:
        return f"{self.code}: {self.message}"


class PstDependencyMissingError(PstError):
    code = "PST_DEPENDENCY_MISSING"
    status_code = 503


class PstCorruptedError(PstError):
    code = "PST_CORRUPTED"
    status_code = 422


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


class LibratomPstArchiveAdapter:
    @staticmethod
    def _load_archive_type() -> Any:
        try:
            from libratom.lib.pff import PffArchive  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover
            raise PstDependencyMissingError(
                "libratom ist nicht installiert. Installiere es mit: pip install libratom"
            ) from exc
        return PffArchive

    def open_archive(self, pst_path: Path) -> Any:
        archive_type = self._load_archive_type()
        archive = archive_type()
        if not hasattr(archive, "load"):
            raise PstCorruptedError("Der PST-Adapter unterstützt keine load()-Methode.")
        try:
            archive.load(str(pst_path))
        except OSError as exc:
            logger.warning("PST konnte nicht geladen werden: %s", pst_path, exc_info=exc)
            raise PstCorruptedError(f"PST beschädigt oder nicht lesbar: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unerwarteter Fehler beim Öffnen der PST: %s", pst_path)
            raise PstCorruptedError(f"PST konnte nicht geöffnet werden: {exc}") from exc
        return archive

    @staticmethod
    def close_archive(archive: Any) -> None:
        close_method = getattr(archive, "close", None)
        if callable(close_method):
            close_method()
            return
        data_obj = getattr(archive, "_data", None)
        data_close = getattr(data_obj, "close", None)
        if callable(data_close):
            data_close()

    @staticmethod
    def get_root_folder(archive: Any) -> Any:
        data_obj = getattr(archive, "_data", None)
        root_folder = getattr(data_obj, "root_folder", None)
        if root_folder is not None:
            return root_folder

        folders_method = getattr(archive, "folders", None)
        if callable(folders_method):
            folder_iter = folders_method()
            try:
                return next(folder_iter)
            except StopIteration as exc:
                raise PstCorruptedError("PST enthält keine Root-Ordnerstruktur.") from exc

        raise PstCorruptedError("Root-Ordner konnte über den PST-Adapter nicht ermittelt werden.")

    @staticmethod
    def get_folder_identifier(folder: Any) -> str:
        identifier = getattr(folder, "identifier", None)
        if identifier is None:
            raise PstCorruptedError("Ordner-Identifier fehlt; stabile node_id kann nicht gebildet werden.")
        return str(identifier)

    @staticmethod
    def get_folder_name(folder: Any, node_id: str) -> str:
        name = _safe_text(getattr(folder, "name", None)).strip()
        return name or f"Ordner-{node_id}"

    @staticmethod
    def get_sub_folders(folder: Any) -> list[Any]:
        sub_folders = getattr(folder, "sub_folders", None)
        if sub_folders is not None:
            return list(sub_folders)

        number_of_sub_folders = getattr(folder, "number_of_sub_folders", None)
        get_sub_folder = getattr(folder, "get_sub_folder", None)
        if isinstance(number_of_sub_folders, int) and callable(get_sub_folder):
            return [get_sub_folder(i) for i in range(number_of_sub_folders)]

        return []

    @staticmethod
    def get_direct_message_count(folder: Any) -> int:
        for attr_name in ("number_of_sub_messages", "number_of_messages"):
            value = getattr(folder, attr_name, None)
            if isinstance(value, int):
                return value
        return 0
