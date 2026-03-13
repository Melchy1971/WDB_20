from fastapi.testclient import TestClient

from app.api.routes import sources as sources_route
from app.models.source_models import Source
from app.models.tree_models import SourceTreeResponse, TreeNode
from app.services import source_selection_service
from main import app

client = TestClient(app)


def _pst_source() -> Source:
    return Source(
        source_id="pst-source-1",
        source_type="PST",
        label="Archiv",
        source_path=r"C:\mail\archive.pst",
        created_at="2026-03-13T10:00:00Z",
    )


def _tree_response() -> SourceTreeResponse:
    return SourceTreeResponse(
        source_id="pst-source-1",
        source_path=r"C:\mail\archive.pst",
        root=TreeNode(
            id="root",
            name="Mailbox",
            path="Mailbox",
            parent_path=None,
            has_children=True,
            message_count=1,
            item_count=3,
            children=[
                TreeNode(
                    id="inbox",
                    name="Inbox",
                    path="Mailbox/Inbox",
                    parent_path="Mailbox",
                    has_children=True,
                    message_count=5,
                    item_count=6,
                    children=[
                        TreeNode(
                            id="projects",
                            name="Projects",
                            path="Mailbox/Inbox/Projects",
                            parent_path="Mailbox/Inbox",
                            has_children=False,
                            message_count=2,
                            item_count=2,
                            children=[],
                        )
                    ],
                )
            ],
        ),
    )


def test_save_selection_returns_node_ids_and_folder_paths(monkeypatch) -> None:
    source_selection_service._store.clear("pst-source-1")  # type: ignore[attr-defined]
    monkeypatch.setattr(sources_route.source_registry_service, "get_source", lambda source_id: _pst_source())
    monkeypatch.setattr(sources_route, "_build_pst_tree_or_raise", lambda pst_path, source_id=None: _tree_response())

    response = client.post(
        "/sources/pst-source-1/selection",
        json={"selected_node_ids": ["inbox", "projects"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["selected_node_ids"] == ["inbox", "projects"]
    assert data["selected_folder_paths"] == ["Mailbox/Inbox", "Mailbox/Inbox/Projects"]
    assert data["selected_count"] == 2


def test_get_selection_sanitizes_against_tree(monkeypatch) -> None:
    source_selection_service._store.clear("pst-source-1")  # type: ignore[attr-defined]
    monkeypatch.setattr(sources_route.source_registry_service, "get_source", lambda source_id: _pst_source())
    monkeypatch.setattr(sources_route, "_build_pst_tree_or_raise", lambda pst_path, source_id=None: _tree_response())
    source_selection_service.set_selection("pst-source-1", ["projects", "ghost"])

    response = client.get("/sources/pst-source-1/selection")

    assert response.status_code == 200
    data = response.json()
    assert data["selected_node_ids"] == ["projects"]
    assert data["selected_folder_paths"] == ["Mailbox/Inbox/Projects"]
    assert data["selected_count"] == 1
