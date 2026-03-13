from app.adapters.pst_archive_adapter import PstCorruptedError, PstDependencyMissingError
from app.api.routes import sources as sources_route
from app.models.tree_models import SourceTreeResponse, TreeNode
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _build_tree_response(source_path: str) -> SourceTreeResponse:
    return SourceTreeResponse(
        source_id=None,
        source_path=source_path,
        root=TreeNode(
            id="root",
            name="Mailbox",
            path="Mailbox",
            parent_path=None,
            has_children=True,
            message_count=3,
            item_count=4,
            children=[
                TreeNode(
                    id="inbox",
                    name="Inbox",
                    path="Mailbox/Inbox",
                    parent_path="Mailbox",
                    has_children=False,
                    message_count=12,
                    item_count=12,
                    children=[],
                )
            ],
        ),
    )


def test_get_pst_tree_endpoint_returns_frontend_friendly_tree(monkeypatch) -> None:
    pst_path = r"\\server\share\archive.pst"

    def fake_build_tree(*, pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
        assert source_id is None
        return _build_tree_response(pst_path)

    monkeypatch.setattr(sources_route.PstParserService, "build_tree", staticmethod(fake_build_tree))

    response = client.get("/sources/pst/tree", params={"path": pst_path})

    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] is None
    assert data["source_path"] == pst_path
    assert data["root"]["path"] == "Mailbox"
    assert data["root"]["children"][0]["parent_path"] == "Mailbox"
    assert data["root"]["children"][0]["message_count"] == 12
    assert data["root"]["children"][0]["has_children"] is False


def test_post_pst_tree_endpoint_returns_tree(monkeypatch) -> None:
    pst_path = r"C:\mail\export.pst"

    def fake_build_tree(*, pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
        return _build_tree_response(pst_path)

    monkeypatch.setattr(sources_route.PstParserService, "build_tree", staticmethod(fake_build_tree))

    response = client.post("/sources/pst/tree", json={"path": pst_path})

    assert response.status_code == 200
    assert response.json()["source_path"] == pst_path


def test_pst_tree_endpoint_rejects_invalid_extension() -> None:
    response = client.get("/sources/pst/tree", params={"path": r"C:\mail\archive.txt"})

    assert response.status_code == 422
    assert response.json()["detail"].startswith("PST_INVALID_PATH:")


def test_pst_tree_endpoint_returns_404_for_missing_file() -> None:
    response = client.get("/sources/pst/tree", params={"path": r"C:\definitely-missing\missing.pst"})

    assert response.status_code == 404
    assert response.json()["detail"].startswith("PST_NOT_FOUND:")


def test_pst_tree_endpoint_returns_503_when_parser_dependency_is_missing(monkeypatch) -> None:
    def fake_build_tree(*, pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
        raise PstDependencyMissingError("libratom fehlt")

    monkeypatch.setattr(sources_route.PstParserService, "build_tree", staticmethod(fake_build_tree))

    response = client.get("/sources/pst/tree", params={"path": r"C:\mail\archive.pst"})

    assert response.status_code == 503
    assert response.json()["detail"].startswith("PST_DEPENDENCY_MISSING:")


def test_pst_tree_endpoint_returns_422_for_corrupted_pst(monkeypatch) -> None:
    def fake_build_tree(*, pst_path: str, source_id: str | None = None) -> SourceTreeResponse:
        raise PstCorruptedError("PST beschädigt oder nicht lesbar")

    monkeypatch.setattr(sources_route.PstParserService, "build_tree", staticmethod(fake_build_tree))

    response = client.get("/sources/pst/tree", params={"path": r"C:\mail\archive.pst"})

    assert response.status_code == 422
    assert response.json()["detail"].startswith("PST_CORRUPTED:")
