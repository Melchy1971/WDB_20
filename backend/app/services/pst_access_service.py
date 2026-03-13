from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path, PureWindowsPath

from app.adapters.pst_archive_adapter import PstError

logger = logging.getLogger(__name__)

PST_ACCESS_TIMEOUT_SECONDS = 8
PST_PARSE_TIMEOUT_SECONDS = 90
NETWORK_WINERRORS = {53, 64, 67, 86, 1219, 1222, 1203, 1231, 1232}


class InvalidPstPathError(PstError):
    code = "PST_INVALID_PATH"
    status_code = 422


class PstFileNotFoundError(PstError):
    code = "PST_NOT_FOUND"
    status_code = 404


class PstAccessDeniedError(PstError):
    code = "PST_ACCESS_DENIED"
    status_code = 403


class PstNetworkPathUnavailableError(PstError):
    code = "PST_NETWORK_UNAVAILABLE"
    status_code = 503


class PstAccessTimeoutError(PstError):
    code = "PST_ACCESS_TIMEOUT"
    status_code = 504


class PstParseTimeoutError(PstError):
    code = "PST_PARSE_TIMEOUT"
    status_code = 504


class PstUnreadableError(PstError):
    code = "PST_UNREADABLE"
    status_code = 422


def _is_unc_path(raw_path: str) -> bool:
    return raw_path.startswith("\\\\")


def _is_supported_windows_absolute_path(raw_path: str) -> bool:
    windows_path = PureWindowsPath(raw_path)
    if not windows_path.is_absolute():
        return False
    return _is_unc_path(raw_path) or (len(windows_path.drive) == 2 and windows_path.drive[1] == ":")


def validate_pst_path(pst_path: str) -> Path:
    normalized_path = pst_path.strip()
    if normalized_path == "":
        raise InvalidPstPathError("Kein PST-Pfad übergeben.")
    if not _is_supported_windows_absolute_path(normalized_path):
        raise InvalidPstPathError(
            "Erwartet wird ein absoluter Windows-Pfad wie D:\\Archiv\\mail.pst oder \\\\server\\freigabe\\mail.pst."
        )

    path = Path(normalized_path)
    if path.suffix.lower() != ".pst":
        raise InvalidPstPathError("Ungültige Dateiendung. Erwartet wird eine .pst-Datei.")
    return path


def _map_os_error(path: Path, exc: OSError) -> PstError:
    winerror = getattr(exc, "winerror", None)
    if isinstance(exc, PermissionError) or winerror == 5:
        return PstAccessDeniedError(f"Zugriff auf PST-Datei verweigert: {path}")
    if winerror in NETWORK_WINERRORS:
        return PstNetworkPathUnavailableError(f"Netzfreigabe nicht erreichbar: {path}")
    if _is_unc_path(str(path)) and "network" in str(exc).lower():
        return PstNetworkPathUnavailableError(f"Netzfreigabe nicht erreichbar: {path}")
    return PstUnreadableError(f"PST-Datei ist nicht lesbar: {path}. Ursache: {exc}")


def _probe_path_sync(path: Path) -> Path:
    try:
        stat_result = path.stat()
    except FileNotFoundError as exc:
        raise PstFileNotFoundError(f"PST-Datei nicht gefunden: {path}") from exc
    except PermissionError as exc:
        raise PstAccessDeniedError(f"Zugriff auf PST-Datei verweigert: {path}") from exc
    except OSError as exc:
        raise _map_os_error(path, exc) from exc

    if not path.is_file():
        raise PstFileNotFoundError(f"PST-Datei nicht gefunden: {path}")

    try:
        with path.open("rb") as file_handle:
            file_handle.read(1)
    except PermissionError as exc:
        raise PstAccessDeniedError(f"Zugriff auf PST-Datei verweigert: {path}") from exc
    except FileNotFoundError as exc:
        raise PstFileNotFoundError(f"PST-Datei nicht gefunden: {path}") from exc
    except OSError as exc:
        raise _map_os_error(path, exc) from exc

    file_size_mb = stat_result.st_size / (1024 * 1024)
    logger.info("PST-Zugriff erfolgreich geprüft", extra={"pst_path": str(path), "size_mb": round(file_size_mb, 2)})
    if file_size_mb >= 1024:
        logger.warning("Sehr große PST-Datei erkannt: %.2f MB (%s)", file_size_mb, path)
    return path


def _run_with_timeout(task_name: str, timeout_seconds: int, func):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func)
    try:
        return future.result(timeout=timeout_seconds)
    except FuturesTimeoutError as exc:
        logger.warning("%s überschritt Timeout von %ss", task_name, timeout_seconds)
        future.cancel()
        raise PstAccessTimeoutError(f"Zeitüberschreitung beim Zugriff auf PST-Datei ({timeout_seconds}s).") from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def validate_and_probe_pst_path(pst_path: str) -> Path:
    path = validate_pst_path(pst_path)
    return _run_with_timeout(
        task_name=f"PST-Preflight {path}",
        timeout_seconds=PST_ACCESS_TIMEOUT_SECONDS,
        func=lambda: _probe_path_sync(path),
    )


def run_pst_parse_with_timeout(parse_callable, pst_path: Path):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(parse_callable)
    try:
        return future.result(timeout=PST_PARSE_TIMEOUT_SECONDS)
    except FuturesTimeoutError as exc:
        logger.warning("PST-Parsing überschritt Timeout von %ss: %s", PST_PARSE_TIMEOUT_SECONDS, pst_path)
        future.cancel()
        raise PstParseTimeoutError(
            f"Zeitüberschreitung beim Einlesen der PST-Struktur ({PST_PARSE_TIMEOUT_SECONDS}s)."
        ) from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
