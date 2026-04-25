import json
from pathlib import Path

import faiss
import numpy as np
import pytest
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("backend/data/faiss_index")
INDEX_FILE = INDEX_DIR / "index.faiss"
METADATA_FILE = INDEX_DIR / "index_metadata.json"


@pytest.mark.requires_index
def test_index_files_exist():
    assert INDEX_FILE.exists(), f"Missing: {INDEX_FILE}"
    assert METADATA_FILE.exists(), f"Missing: {METADATA_FILE}"


@pytest.mark.requires_index
def test_index_loads():
    index = faiss.read_index(str(INDEX_FILE))
    assert index.ntotal > 0, "FAISS index contains no vectors"


@pytest.mark.requires_index
def test_metadata_structure():
    with open(METADATA_FILE) as f:
        metadata = json.load(f)

    assert isinstance(metadata, list), "Metadata must be a list"
    assert len(metadata) > 0, "Metadata list is empty"

    required_keys = {"source", "principle", "text"}
    for i, item in enumerate(metadata):
        missing = required_keys - item.keys()
        assert not missing, f"Item {i} missing keys: {missing}"


@pytest.mark.requires_index
def test_query_returns_results():
    index = faiss.read_index(str(INDEX_FILE))

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query = "progressive overload training volume"
    emb = model.encode([query])
    emb = np.array(emb, dtype=np.float32)
    faiss.normalize_L2(emb)

    distances, indices = index.search(emb, k=3)

    assert indices.shape == (1, 3), "Expected 3 results"
    assert all(d > 0 for d in distances[0]), "All distances must be > 0"


@pytest.mark.requires_index
def test_grip_knowledge_retrievable():
    index = faiss.read_index(str(INDEX_FILE))
    with open(METADATA_FILE) as f:
        metadata = json.load(f)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query = "gripper close training"
    emb = model.encode([query])
    emb = np.array(emb, dtype=np.float32)
    faiss.normalize_L2(emb)

    distances, indices = index.search(emb, k=5)

    sources = [metadata[idx]["source"] for idx in indices[0]]
    assert any("grip" in s for s in sources), (
        f"No grip-related result in top-5. Sources: {sources}"
    )
