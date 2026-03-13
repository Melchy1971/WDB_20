from datetime import datetime, timezone

from app.models.pst_import_models import ImportRun
from app.services.pst_import_service import calculate_progress_percent


def _build_run() -> ImportRun:
    return ImportRun(
        import_run_id="run-progress",
        source_id="source-1",
        source_path=r"C:\mail\archive.pst",
        selected_node_ids=["a", "b"],
        selected_folder_paths=["Mailbox", "Mailbox/Inbox"],
        status="running",
        started_at=datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc),
        total_folder_count=2,
        processed_folder_count=1,
        total_message_count_estimate=8,
        processed_message_count=3,
    )


def test_calculate_progress_percent_uses_folders_and_messages() -> None:
    run = _build_run()
    assert calculate_progress_percent(run) == 40.0


def test_calculate_progress_percent_returns_none_for_unknown_total_while_running() -> None:
    run = _build_run().model_copy(
        update={
            "total_folder_count": 0,
            "processed_folder_count": 0,
            "total_message_count_estimate": 0,
            "processed_message_count": 0,
        }
    )
    assert calculate_progress_percent(run) is None


def test_calculate_progress_percent_returns_100_for_finished_run_without_totals() -> None:
    run = _build_run().model_copy(
        update={
            "status": "finished",
            "total_folder_count": 0,
            "processed_folder_count": 0,
            "total_message_count_estimate": 0,
            "processed_message_count": 0,
        }
    )
    assert calculate_progress_percent(run) == 100.0
