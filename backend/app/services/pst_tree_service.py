"""
pst_tree_service — Delegiert an pst_parser_service (pypff-basierter Parser).

Dieser Service ist die Brücke zwischen dem HTTP-Layer (sources.py-Route)
und dem eigentlichen Parser. Er löst die Source-Path über die Registry auf
und leitet den Aufruf weiter.
"""

from fastapi import HTTPException

from app.models.tree_models import SourceTreeResponse
from app.services import source_registry_service
from app.services import pst_parser_service


def get_pst_tree(source_id: str) -> SourceTreeResponse:
    """
    Lädt den Ordnerbaum der PST-Datei, die der Source *source_id* zugeordnet ist.

    Raises:
        HTTPException 404 — Source nicht gefunden.
        HTTPException 422 — PST-Datei nicht gefunden oder nicht lesbar.
        HTTPException 503 — pypff nicht installiert.
    """
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Quelle nicht gefunden: {source_id}")

    try:
        return pst_parser_service.parse_pst_tree(
            pst_path=source.source_path,
            source_id=source_id,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"PST-Parser nicht verfügbar: {exc}",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"PST-Datei konnte nicht gelesen werden: {exc}",
        ) from exc
