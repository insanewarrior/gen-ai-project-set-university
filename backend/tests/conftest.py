import pytest
from fastapi.testclient import TestClient

from main import app

FAISS_INDEX_DIR = "backend/data/faiss_index"
FAISS_INDEX_FILE = f"{FAISS_INDEX_DIR}/index.faiss"
FAISS_METADATA_FILE = f"{FAISS_INDEX_DIR}/index_metadata.json"


@pytest.fixture
def client():
    return TestClient(app)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_index: requires FAISS index to be built",
    )


def pytest_collection_modifyitems(config, items):
    import os

    index_missing = not (
        os.path.exists(FAISS_INDEX_FILE)
        and os.path.exists(FAISS_METADATA_FILE)
    )
    skip_marker = pytest.mark.skip(
        reason=(
            "FAISS index not built — run: "
            "python backend/scripts/build_faiss_index.py"
        )
    )
    for item in items:
        if "requires_index" in item.keywords and index_missing:
            item.add_marker(skip_marker)
