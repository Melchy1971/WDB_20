from app.adapters.pst_archive_adapter import PstError
from app.services import pst_access_service


def test_validate_pst_path_accepts_drive_letter() -> None:
    path = pst_access_service.validate_pst_path(r"D:\Archive\mail.pst")
    assert str(path) == r"D:\Archive\mail.pst"


def test_validate_pst_path_accepts_unc_path() -> None:
    path = pst_access_service.validate_pst_path(r"\\server\freigabe\mail.pst")
    assert str(path) == r"\\server\freigabe\mail.pst"


def test_validate_pst_path_rejects_relative_path() -> None:
    try:
        pst_access_service.validate_pst_path(r"archive\mail.pst")
    except PstError as exc:
        assert exc.code == "PST_INVALID_PATH"
        assert exc.status_code == 422
    else:
        raise AssertionError("Expected PstError for relative path")


def test_map_os_error_returns_network_error_for_unc_share() -> None:
    error = OSError("network path missing")
    error.winerror = 53  # type: ignore[attr-defined]

    mapped = pst_access_service._map_os_error(  # type: ignore[attr-defined]
        pst_access_service.validate_pst_path(r"\\server\freigabe\mail.pst"),
        error,
    )

    assert mapped.code == "PST_NETWORK_UNAVAILABLE"
    assert mapped.status_code == 503


def test_map_os_error_returns_access_denied() -> None:
    error = PermissionError("access denied")
    mapped = pst_access_service._map_os_error(  # type: ignore[attr-defined]
        pst_access_service.validate_pst_path(r"E:\Archive\mail.pst"),
        error,
    )

    assert mapped.code == "PST_ACCESS_DENIED"
    assert mapped.status_code == 403
