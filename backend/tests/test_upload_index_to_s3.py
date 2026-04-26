"""Unit tests for backend/scripts/upload_index_to_s3.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import scripts.upload_index_to_s3 as upl


# ---------------------------------------------------------------------------
# Task 2.2 — missing S3_BUCKET env var → sys.exit(1)
# ---------------------------------------------------------------------------


def test_main_missing_s3_bucket_exits(monkeypatch):
    monkeypatch.delenv("S3_BUCKET", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        upl.main()
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Task 2.3 — missing local index files → sys.exit(1)
# ---------------------------------------------------------------------------


def test_main_missing_index_files_exits(tmp_path, monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    empty_dir = tmp_path / "faiss_index"
    empty_dir.mkdir()

    mock_s3 = MagicMock()
    with (
        patch("boto3.client", return_value=mock_s3),
        patch.object(upl, "INDEX_DIR", empty_dir),
        pytest.raises(SystemExit) as exc_info,
    ):
        upl.main()

    assert exc_info.value.code == 1
    mock_s3.upload_file.assert_not_called()


# ---------------------------------------------------------------------------
# Task 2.4 — happy path: mocked boto3, verify upload_file calls
# ---------------------------------------------------------------------------


def test_main_happy_path_uploads_both_files(tmp_path, monkeypatch):
    bucket = "my-faiss-bucket"
    monkeypatch.setenv("S3_BUCKET", bucket)

    index_dir = tmp_path / "faiss_index"
    index_dir.mkdir()
    (index_dir / "index.faiss").write_bytes(b"fake-faiss-data")
    (index_dir / "index_metadata.json").write_text('[]')

    mock_s3 = MagicMock()
    with (
        patch("boto3.client", return_value=mock_s3),
        patch.object(upl, "INDEX_DIR", index_dir),
    ):
        upl.main()

    assert mock_s3.upload_file.call_count == 2
    expected_calls = [
        call(str(index_dir / "index.faiss"), bucket, "faiss_index/index.faiss"),
        call(str(index_dir / "index_metadata.json"), bucket, "faiss_index/index_metadata.json"),
    ]
    mock_s3.upload_file.assert_has_calls(expected_calls, any_order=False)
