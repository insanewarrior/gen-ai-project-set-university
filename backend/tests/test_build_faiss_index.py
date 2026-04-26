"""Unit tests for backend/scripts/build_faiss_index.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.build_faiss_index import chunk_document


# ---------------------------------------------------------------------------
# Task 1.2 — chunk_document(): schema, min-length filter, ## splitting
# ---------------------------------------------------------------------------


def test_chunk_document_schema_and_splitting(tmp_path):
    md = tmp_path / "test.md"
    md.write_text(
        "## Section One\n\n"
        "This is a paragraph that is definitely longer than fifty characters total.\n\n"
        "## Section Two\n\n"
        "Another paragraph here which is also longer than fifty characters long.\n"
    )
    chunks = chunk_document(md)
    assert len(chunks) == 2
    for chunk in chunks:
        assert set(chunk.keys()) == {"source", "principle", "text"}
        assert chunk["source"] == "test.md"
    assert chunks[0]["principle"] == "Section One"
    assert chunks[1]["principle"] == "Section Two"


def test_chunk_document_min_length_filter(tmp_path):
    md = tmp_path / "kb.md"
    md.write_text(
        "## Header\n\n"
        "Short.\n\n"  # < 50 chars, should be excluded
        "This paragraph is definitely longer than fifty characters so it passes the filter.\n"
    )
    chunks = chunk_document(md)
    assert len(chunks) == 1
    assert len(chunks[0]["text"]) >= 50


# ---------------------------------------------------------------------------
# Task 1.3 — chunk_document(): no ## headers → filename as principle
# ---------------------------------------------------------------------------


def test_chunk_document_no_headers_uses_filename_as_principle(tmp_path):
    md = tmp_path / "myfile.md"
    md.write_text(
        "This is a long paragraph with no section headers at all, exceeding fifty chars.\n\n"
        "Another paragraph that also has enough characters to pass the minimum length filter here."
    )
    chunks = chunk_document(md)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["principle"] == "myfile"
        assert chunk["source"] == "myfile.md"


# ---------------------------------------------------------------------------
# Task 1.4 — main(): end-to-end with mocked SentenceTransformer
# ---------------------------------------------------------------------------


def test_main_creates_index_and_metadata(tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    output_dir = tmp_path / "faiss_index"

    (knowledge_dir / "topic.md").write_text(
        "## Training Basics\n\n"
        "Progressive overload is the gradual increase of stress placed upon the body during training.\n\n"
        "## Recovery\n\n"
        "Adequate rest between sessions is essential for strength adaptation and muscle growth.\n"
    )

    def fake_encode(texts, **kwargs):
        return np.random.rand(len(texts), 384).astype(np.float32)

    mock_model = MagicMock()
    mock_model.encode.side_effect = fake_encode

    import scripts.build_faiss_index as bfi

    with (
        patch.object(bfi, "KNOWLEDGE_DIR", knowledge_dir),
        patch.object(bfi, "OUTPUT_DIR", output_dir),
        patch("scripts.build_faiss_index.SentenceTransformer", return_value=mock_model),
    ):
        bfi.main()

    assert (output_dir / "index.faiss").exists()
    assert (output_dir / "index_metadata.json").exists()

    metadata = json.loads((output_dir / "index_metadata.json").read_text())
    assert len(metadata) == 2
    for entry in metadata:
        assert set(entry.keys()) == {"source", "principle", "text"}


def test_main_metadata_count_equals_chunk_count(tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    output_dir = tmp_path / "faiss_index"

    doc = "## A\n\n" + ("x" * 60 + "\n\n") * 3
    (knowledge_dir / "doc.md").write_text(doc)

    def fake_encode(texts, **kwargs):
        return np.random.rand(len(texts), 384).astype(np.float32)

    mock_model = MagicMock()
    mock_model.encode.side_effect = fake_encode

    import scripts.build_faiss_index as bfi

    with (
        patch.object(bfi, "KNOWLEDGE_DIR", knowledge_dir),
        patch.object(bfi, "OUTPUT_DIR", output_dir),
        patch("scripts.build_faiss_index.SentenceTransformer", return_value=mock_model),
    ):
        bfi.main()

    metadata = json.loads((output_dir / "index_metadata.json").read_text())
    chunks = chunk_document(knowledge_dir / "doc.md")
    assert len(metadata) == len(chunks)


# ---------------------------------------------------------------------------
# Task 1.5 — main() errors
# ---------------------------------------------------------------------------


def test_main_missing_knowledge_dir_exits(tmp_path):
    missing_dir = tmp_path / "nonexistent"
    output_dir = tmp_path / "faiss_index"

    import scripts.build_faiss_index as bfi

    with (
        patch.object(bfi, "KNOWLEDGE_DIR", missing_dir),
        patch.object(bfi, "OUTPUT_DIR", output_dir),
        pytest.raises(SystemExit) as exc_info,
    ):
        bfi.main()

    assert exc_info.value.code == 1


def test_main_empty_knowledge_dir_exits(tmp_path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    output_dir = tmp_path / "faiss_index"

    import scripts.build_faiss_index as bfi

    with (
        patch.object(bfi, "KNOWLEDGE_DIR", knowledge_dir),
        patch.object(bfi, "OUTPUT_DIR", output_dir),
        pytest.raises(SystemExit) as exc_info,
    ):
        bfi.main()

    assert exc_info.value.code == 1
