import os
import string
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.models.filesystem_models import FilesystemBrowseResponse, FilesystemEntry

router = APIRouter(prefix="/filesystem", tags=["filesystem"])


def _list_drives() -> list[FilesystemEntry]:
    drives: list[FilesystemEntry] = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(FilesystemEntry(name=drive, path=drive, is_dir=True))
    return drives


@router.get("/browse", response_model=FilesystemBrowseResponse)
def browse_filesystem(path: str = Query(default="")) -> FilesystemBrowseResponse:
    stripped = path.strip()

    # Laufwerksübersicht
    if not stripped:
        return FilesystemBrowseResponse(
            current_path="",
            parent_path=None,
            entries=_list_drives(),
        )

    p = Path(stripped)

    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Pfad nicht gefunden: {stripped}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Kein Verzeichnis: {stripped}")

    # parent_path: "" = zurück zur Laufwerksübersicht (wenn Laufwerkswurzel)
    is_root = p.parent == p
    if is_root:
        parent_path: str | None = ""
    else:
        parent_path = str(p.parent)

    entries: list[FilesystemEntry] = []
    try:
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for item in items:
            try:
                is_dir = item.is_dir()
                if is_dir or item.suffix.lower() == ".pst":
                    entries.append(FilesystemEntry(
                        name=item.name,
                        path=str(item),
                        is_dir=is_dir,
                    ))
            except PermissionError:
                continue
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=f"Zugriff verweigert: {stripped}") from exc

    return FilesystemBrowseResponse(
        current_path=str(p),
        parent_path=parent_path,
        entries=entries,
    )
