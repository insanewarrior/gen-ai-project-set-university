# Story 6.2: Knowledge Base Update Pipeline

Status: review

## Story

As an **operator**,
I want to rebuild and deploy an updated FAISS index without system downtime,
So that I can add new knowledge sources and improve coaching quality continuously.

## Acceptance Criteria

1. **Given** I have added new source documents to `backend/data/knowledge/`
   **When** I run `python backend/scripts/build_faiss_index.py` followed by `python backend/scripts/upload_index_to_s3.py`
   **Then** a new FAISS index is built, uploaded to S3, and Lambda instances pick up the updated index on their next cold start (FR32, NFR23)

2. **Given** Lambda instances are currently serving queries with the old index
   **When** the new index is uploaded to S3
   **Then** existing Lambda instances continue serving with the old index until their next cold start — no downtime, no errors, no manual intervention required

3. **Given** the index rebuild process
   **When** it completes
   **Then** the new index contains all previously indexed content plus the new documents, with no content loss

---

## Critical Context: What Already Exists — DO NOT RECREATE

### Scripts Already Implemented (DO NOT REWRITE)

**`backend/scripts/build_faiss_index.py`** — FULLY IMPLEMENTED AND WORKING:
- Reads all `.md` files from `backend/data/knowledge/` (recursive glob)
- Chunks by `## ` headers, then by double-newline paragraphs (min 50 chars)
- Chunk schema: `{"source": filename, "principle": header_text, "text": paragraph}`
- Model: `all-MiniLM-L6-v2` (sentence-transformers), 384-dim embeddings, `faiss.normalize_L2`
- Index type: `faiss.IndexFlatIP` (inner-product after L2-normalize = cosine similarity)
- Outputs: `backend/data/faiss_index/index.faiss` + `backend/data/faiss_index/index_metadata.json`
- Run from project root: `python backend/scripts/build_faiss_index.py`

**`backend/scripts/upload_index_to_s3.py`** — FULLY IMPLEMENTED AND WORKING:
- Requires `S3_BUCKET` env var (exits with error if not set)
- Uploads `index.faiss` + `index_metadata.json` to `s3://{bucket}/faiss_index/`
- Uses `boto3.client("s3").upload_file()`
- Run from project root: `S3_BUCKET=<name> python backend/scripts/upload_index_to_s3.py`

### Makefile Already Has `build-index` Target
```makefile
build-index:
    python backend/scripts/build_faiss_index.py
```
No `upload-index` or combined `update-kb` target exists yet — **add these**.

### RAG Service Already Handles S3 Download on Cold Start
`backend/services/rag_service.py::_download_from_s3()`:
- On Lambda cold start: if `/tmp/data/faiss_index/index.faiss` doesn't exist, downloads from `config.S3_FAISS_BUCKET`
- Config: `FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")` (relative to backend CWD)
- Config: `S3_FAISS_BUCKET = os.getenv("S3_FAISS_BUCKET")` — set in CDK stack (`faiss_bucket.bucket_name`)
- CDK output `FaissIndexBucketName` gives the bucket name for operator use

### Existing Tests (DO NOT DUPLICATE)
`backend/tests/test_faiss_index.py` — marked `@pytest.mark.requires_index`:
- `test_index_files_exist()` — checks index.faiss + index_metadata.json present
- `test_index_loads()` — reads index, asserts ntotal > 0
- `test_metadata_structure()` — validates keys: `source`, `principle`, `text`
- `test_query_returns_results()` — end-to-end cosine search
- `test_grip_knowledge_retrievable()` — domain-specific retrieval check

These tests auto-skip when index is missing (see `conftest.pytest_collection_modifyitems`).

### Current Knowledge Base
`backend/data/knowledge/`: 6 files — `armwrestling.md`, `cross_domain.md`, `grip_sport.md`, `periodization.md`, `powerlifting.md`, `progressive_overload.md`

---

## What This Story Actually Needs (Do Not Over-Engineer)

The scripts and RAG service are complete. The no-downtime property is inherent (S3 atomic overwrite + Lambda cold start). This story's implementation work is:

1. **Add unit tests for `build_faiss_index.py`** — test the `chunk_document()` function and the full pipeline with a temp directory (no model load needed for chunking tests; use the model for integration test)
2. **Add unit tests for `upload_index_to_s3.py`** — mock `boto3` to avoid AWS calls
3. **Add `upload-index` and `update-kb` Makefile targets** — operator convenience
4. **Run full regression** — no backend logic changed, so all existing tests should pass

---

## Tasks / Subtasks

- [x] Task 1: Add unit tests for `build_faiss_index.py`
  - [x] 1.1: Create `backend/tests/test_build_faiss_index.py`
  - [x] 1.2: Test `chunk_document()` with a temp markdown file — verify chunk schema `{source, principle, text}`, verify min-length filter (< 50 chars excluded), verify `## ` splitting
  - [x] 1.3: Test `chunk_document()` with a file that has no `## ` headers — should use filename as principle
  - [x] 1.4: Test `main()` end-to-end with a temp knowledge dir and temp output dir — mock `SentenceTransformer` to avoid model download (monkeypatch or pytest fixture). Verify `index.faiss` and `index_metadata.json` are created. Verify metadata count equals chunk count.
  - [x] 1.5: Test `main()` errors: missing knowledge dir → sys.exit(1); empty dir (no .md files) → sys.exit(1)

- [x] Task 2: Add unit tests for `upload_index_to_s3.py`
  - [x] 2.1: Create `backend/tests/test_upload_index_to_s3.py`
  - [x] 2.2: Test `main()` missing `S3_BUCKET` env var → sys.exit(1) (use `monkeypatch.delenv`)
  - [x] 2.3: Test `main()` missing local index files → sys.exit(1) (use temp dir without files)
  - [x] 2.4: Test `main()` happy path — mock `boto3.client("s3")`, provide `S3_BUCKET` env var and temp index dir with stub files. Verify `upload_file` called once per file with correct args: `(local_path, bucket, "faiss_index/{filename}")`

- [x] Task 3: Add Makefile targets
  - [x] 3.1: Add `upload-index` target: simple `python backend/scripts/upload_index_to_s3.py` with comment that `S3_BUCKET` must be set
  - [x] 3.2: Add `update-kb` target that runs `build-index` then `upload-index` in sequence
  - [x] 3.3: Add `upload-index` and `update-kb` to `.PHONY`

- [x] Task 4: Run full regression
  - [x] 4.1: `pytest backend/tests/` — all 83 tests pass (10 new + 73 existing)
  - [x] 4.2: Confirm `requires_index` tests still auto-skip when run in CI without built index

---

## Dev Notes

### Test File Locations Must Match Project Pattern
All backend tests are in `backend/tests/`. New test files go there. Import the script modules using `sys.path` manipulation or by running scripts as subprocesses. The scripts use relative paths (`Path("backend/data/knowledge")`), so tests that test `main()` must either run from project root or monkeypatch the path constants.

### Recommended Test Approach for build_faiss_index.py
The `chunk_document()` function is pure and importable. Test it directly. For `main()`, monkeypatch `KNOWLEDGE_DIR` and `OUTPUT_DIR` to temp directories, and monkeypatch `SentenceTransformer` to return pre-built numpy arrays (avoid 80MB model download in CI).

```python
import numpy as np
from unittest.mock import MagicMock, patch

mock_model = MagicMock()
mock_model.encode.return_value = np.random.rand(N, 384).astype(np.float32)

with patch("scripts.build_faiss_index.SentenceTransformer", return_value=mock_model):
    ...
```

Note: script imports are relative to `backend/` directory. Run tests from project root with `PYTHONPATH=backend pytest backend/tests/`.

### Recommended Test Approach for upload_index_to_s3.py
Mock at the `boto3.client` level:
```python
from unittest.mock import MagicMock, patch

mock_s3 = MagicMock()
with patch("boto3.client", return_value=mock_s3):
    main()
    assert mock_s3.upload_file.call_count == 2
```

### Makefile `upload-index` Target — Keep Simple
The Makefile uses simple shell commands. For `upload-index`, the operator must export `S3_BUCKET` before running. Add a comment explaining this:

```makefile
upload-index:
	@echo "Requires S3_BUCKET env var. Get it from CDK output FaissIndexBucketName."
	python backend/scripts/upload_index_to_s3.py

update-kb: build-index upload-index
```

### No-Downtime Is Inherent — No Code Required
NFR23 (hot FAISS reload via cold start) is satisfied by the existing architecture:
- S3 `upload_file` is atomic — in-progress Lambda invocations read from `/tmp` cache and are unaffected
- New Lambda instances download the new index on their next cold start
- No Lambda function update or deployment needed — just S3 overwrite
- Architecture doc explicitly confirms: "FAISS hot reload: natural cold start rotation sufficient at capstone scale"

### Running Scripts from Project Root
Both scripts use paths relative to the project root (`Path("backend/data/...")`). Always run from project root:
```bash
python backend/scripts/build_faiss_index.py
S3_BUCKET=<bucket-name> python backend/scripts/upload_index_to_s3.py
```
Or use `make build-index` / `make upload-index` / `make update-kb`.

### CDK Stack Output for Bucket Name
After `cdk deploy`, the bucket name is in CDK output `FaissIndexBucketName`. Operator retrieves it with:
```bash
aws cloudformation describe-stacks --stack-name StrengthwiseStack \
  --query "Stacks[0].Outputs[?OutputKey=='FaissIndexBucketName'].OutputValue" \
  --output text
```

### pytest conftest.py `requires_index` Auto-Skip
Tests marked `@pytest.mark.requires_index` auto-skip when `backend/data/faiss_index/index.faiss` is missing. The new tests (build/upload scripts) should NOT use this marker — they use temp dirs and mocks, so they run in any environment.

### Backend venv Location
Backend dependencies (faiss-cpu, sentence-transformers, boto3) are in `backend/.venv` or the project venv. Run `source backend/.venv/bin/activate` before running scripts or tests if needed.

---

## Project Structure Notes

Files to CREATE:
```
backend/tests/test_build_faiss_index.py   ← NEW: unit tests for build script
backend/tests/test_upload_index_to_s3.py  ← NEW: unit tests for upload script
```

Files to MODIFY:
```
Makefile  ← ADD upload-index and update-kb targets; ADD to .PHONY
```

Files NOT to touch (already complete):
```
backend/scripts/build_faiss_index.py      ← DO NOT MODIFY
backend/scripts/upload_index_to_s3.py     ← DO NOT MODIFY
backend/services/rag_service.py           ← DO NOT MODIFY
backend/tests/test_faiss_index.py         ← DO NOT MODIFY
backend/tests/conftest.py                 ← DO NOT MODIFY
infra/stacks/strengthwise_stack.py        ← DO NOT MODIFY
```

### References

- Architecture: `_bmad-output/planning-artifacts/architecture.md` — FAISS_INDEX_PATH, S3_FAISS_BUCKET config vars; "FAISS hot reload: natural cold start rotation sufficient at capstone scale"; `FaissIndexBucketName` CDK output
- PRD FR32: "The operator can update the general knowledge base (rebuild FAISS index) without system downtime"
- PRD NFR23: "The FAISS index can be rebuilt and redeployed to S3 without downtime — Lambda picks up the updated index on next cold start"
- Build script: `backend/scripts/build_faiss_index.py`
- Upload script: `backend/scripts/upload_index_to_s3.py`
- RAG service S3 download: `backend/services/rag_service.py::_download_from_s3`
- Existing index tests: `backend/tests/test_faiss_index.py`
- CDK stack FAISS bucket: `infra/stacks/strengthwise_stack.py` line 98, 121, 129, 226
- Previous story (6-1): `_bmad-output/implementation-artifacts/6-1-system-usage-monitoring.md`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Created `backend/tests/test_build_faiss_index.py` (7 tests): covers `chunk_document()` schema/splitting/min-length/no-headers, `main()` end-to-end with mocked SentenceTransformer (verifies index.faiss + index_metadata.json creation, metadata count == chunk count), and `main()` error paths (missing dir → exit(1), empty dir → exit(1)).
- Created `backend/tests/test_upload_index_to_s3.py` (3 tests): covers missing S3_BUCKET → exit(1), missing local files → exit(1), happy path verifying `upload_file` called twice with correct (local_path, bucket, s3_key) args.
- Updated `Makefile`: added `upload-index` (with operator guidance comment) and `update-kb: build-index upload-index` targets; added both to `.PHONY`.
- Full suite: 83/83 tests pass, zero regressions. `requires_index` tests pass (index present locally) and auto-skip in CI when index missing.

### File List

- `backend/tests/test_build_faiss_index.py` — NEW
- `backend/tests/test_upload_index_to_s3.py` — NEW
- `Makefile` — MODIFIED (upload-index, update-kb targets + .PHONY)

### Change Log

- 2026-04-26: Added unit tests for build_faiss_index.py (7 tests) and upload_index_to_s3.py (3 tests); added upload-index and update-kb Makefile targets. All 83 tests pass.
