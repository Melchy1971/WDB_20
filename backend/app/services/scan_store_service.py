from app.models.document_models import ParsedDocument


class _ScanStore:
    """In-Memory-Speicher für gescannte Dokumente — indiziert nach scan_id und document_id."""

    def __init__(self) -> None:
        self._scans: dict[str, dict[str, ParsedDocument]] = {}

    def new_scan(self, scan_id: str) -> None:
        self._scans[scan_id] = {}

    def put(self, scan_id: str, document: ParsedDocument) -> None:
        if scan_id not in self._scans:
            self._scans[scan_id] = {}
        self._scans[scan_id][document.document_id] = document

    def get(self, scan_id: str, document_id: str) -> ParsedDocument | None:
        scan = self._scans.get(scan_id)
        if scan is None:
            return None
        return scan.get(document_id)

    def list_documents(self, scan_id: str) -> list[ParsedDocument]:
        scan = self._scans.get(scan_id)
        if scan is None:
            return []
        return list(scan.values())

    def clear(self) -> None:
        self._scans.clear()


_store = _ScanStore()


def new_scan(scan_id: str) -> None:
    _store.new_scan(scan_id)


def put(scan_id: str, document: ParsedDocument) -> None:
    _store.put(scan_id, document)


def get(scan_id: str, document_id: str) -> ParsedDocument | None:
    return _store.get(scan_id, document_id)


def list_documents(scan_id: str) -> list[ParsedDocument]:
    return _store.list_documents(scan_id)


def clear() -> None:
    _store.clear()
