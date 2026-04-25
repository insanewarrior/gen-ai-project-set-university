# Story 3.1: Knowledge Base Ingestion & FAISS Index

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **operator**,
I want to ingest the curated strength science corpus into a FAISS vector index,
so that the AI coaching system has a searchable general knowledge base to cite from.

## Acceptance Criteria

1. **Given** knowledge base source documents exist in `backend/data/knowledge/` **When** I run `python backend/scripts/build_faiss_index.py` **Then** the script embeds all documents using sentence-transformers (`all-MiniLM-L6-v2`), produces `index.faiss` and `index_metadata.json`, and saves them to `backend/data/faiss_index/`

2. **Given** a built FAISS index **When** I query it with a strength training concept (e.g., "progressive overload periodization") **Then** it returns top-K relevant chunks with source attribution — `{ source, principle, text }` (FR24)

3. **Given** the FAISS index **When** I inspect its size **Then** it is under 50MB total (index.faiss + metadata), well within Lambda's 128-512MB memory allocation (NFR16)

4. **Given** a local FAISS index exists in `backend/data/faiss_index/` **When** I run `python backend/scripts/upload_index_to_s3.py` **Then** `index.faiss` and `index_metadata.json` are uploaded to the S3 bucket key prefix `faiss_index/` for Lambda cold-start consumption

5. **Given** the knowledge corpus **When** I inspect the indexed content **Then** it covers: periodization principles, progressive overload, sport-specific programming for grip sport, armwrestling, and powerlifting, and cross-domain transfer knowledge (FR24, FR26)

6. **Given** a `pytest backend/tests/test_faiss_index.py` run **When** the FAISS index exists locally **Then** all tests pass: index loads, a sample query returns ≥1 relevant result, metadata has correct structure

## Tasks / Subtasks

- [x] Task 1: Create knowledge base markdown documents (AC: #5)
  - [x] 1.1: Create `backend/data/knowledge/` directory
  - [x] 1.2: Create `backend/data/knowledge/periodization.md` — covers linear, undulating, and block periodization; volume/intensity waves; peaking protocols
  - [x] 1.3: Create `backend/data/knowledge/progressive_overload.md` — progressive overload principles, Prilepin's Chart (intensity zones: 70-79%: 18-24 reps, 80-89%: 15-20 reps, 90%+: 4-10 reps), SRA curve
  - [x] 1.4: Create `backend/data/knowledge/powerlifting.md` — squat/bench/deadlift programming, competition peaking, accessory selection, frequency recommendations
  - [x] 1.5: Create `backend/data/knowledge/grip_sport.md` — gripper training (RGC, CoC), hub/pinch specificity, wrist conditioning, peak timing before competitions
  - [x] 1.6: Create `backend/data/knowledge/armwrestling.md` — pronation/supination strength, side pressure vs hook technique, cupping, sport-specific strength transfer
  - [x] 1.7: Create `backend/data/knowledge/cross_domain.md` — how powerlifting peaking applies to armwrestling/grip, tendon adaptation timelines, general strength foundations common to all disciplines
  - [x] 1.8: Each document: 400-800 words, factual, uses clear section headers (##), written so chunking at section boundaries yields coherent self-contained passages

- [x] Task 2: Write `build_faiss_index.py` script (AC: #1, #2, #3)
  - [x] 2.1: Create `backend/scripts/build_faiss_index.py`
  - [x] 2.2: Load all `.md` files from `backend/data/knowledge/` — use `pathlib.Path` to glob `**/*.md`
  - [x] 2.3: Chunking strategy: split each document at `##` section headers. Each chunk = {source_file, section_header, text}. If a section exceeds 600 chars, further split at paragraph breaks (double newline). Min chunk size: 50 chars (skip shorter).
  - [x] 2.4: Embed all chunks via `SentenceTransformer("all-MiniLM-L6-v2")` — model auto-downloads on first run. Call `model.encode(texts, batch_size=32, show_progress_bar=True)`. Returns numpy array shape `(N, 384)`.
  - [x] 2.5: Normalize embeddings for cosine similarity: `faiss.normalize_L2(embeddings)`. Use `faiss.IndexFlatIP` (inner product on normalized vectors = cosine similarity).
  - [x] 2.6: Build index: `index = faiss.IndexFlatIP(384)` then `index.add(embeddings)`.
  - [x] 2.7: Build `index_metadata.json`: list of dicts in chunk order — `[{ "source": "grip_sport.md", "principle": "Section Header", "text": "chunk text..." }, ...]`. Index position in the list = FAISS vector id.
  - [x] 2.8: Save outputs: `faiss.write_index(index, "backend/data/faiss_index/index.faiss")` and `json.dump(metadata, open("backend/data/faiss_index/index_metadata.json", "w"), indent=2)`.
  - [x] 2.9: Create `backend/data/faiss_index/` directory if it doesn't exist (`Path.mkdir(parents=True, exist_ok=True)`).
  - [x] 2.10: Print summary on completion: `Built FAISS index with N chunks from K documents. Index size: X bytes.`
  - [x] 2.11: Script is runnable from repo root: `python backend/scripts/build_faiss_index.py`

- [x] Task 3: Write `upload_index_to_s3.py` script (AC: #4)
  - [x] 3.1: Create `backend/scripts/upload_index_to_s3.py`
  - [x] 3.2: Read S3 bucket name from `S3_BUCKET` env var (fail with clear error if missing)
  - [x] 3.3: Upload `backend/data/faiss_index/index.faiss` → `s3://{S3_BUCKET}/faiss_index/index.faiss`
  - [x] 3.4: Upload `backend/data/faiss_index/index_metadata.json` → `s3://{S3_BUCKET}/faiss_index/index_metadata.json`
  - [x] 3.5: Use `boto3.client("s3").upload_file()` — same boto3 already in requirements.txt
  - [x] 3.6: Print upload confirmation for each file with S3 path

- [x] Task 4: Write pytest tests for FAISS index (AC: #6)
  - [x] 4.1: Create `backend/tests/test_faiss_index.py`
  - [x] 4.2: `test_index_files_exist`: assert `backend/data/faiss_index/index.faiss` and `index_metadata.json` exist
  - [x] 4.3: `test_index_loads`: load index with `faiss.read_index(...)`, assert `index.ntotal > 0`
  - [x] 4.4: `test_metadata_structure`: load JSON, assert it's a list, assert each item has keys `source`, `principle`, `text`
  - [x] 4.5: `test_query_returns_results`: embed "progressive overload training volume" with all-MiniLM-L6-v2, normalize, search with `k=3`, assert 3 results returned with distances > 0
  - [x] 4.6: `test_grip_knowledge_retrievable`: query "gripper close training", assert at least one result has `source` containing "grip"
  - [x] 4.7: Mark tests with `@pytest.mark.requires_index` — add to `conftest.py` so they can be skipped if index doesn't exist yet (use `pytest.ini` or `conftest.py` skip condition)
  - [x] 4.8: **DO NOT use moto** — these tests load the real FAISS index from filesystem, no DynamoDB involved

- [x] Task 5: Add `__init__.py` to `backend/scripts/` if missing and verify script runability (AC: #1)
  - [x] 5.1: Check if `backend/scripts/` exists — it doesn't yet; create it
  - [x] 5.2: Scripts are standalone executables (not imported as modules) — no `__init__.py` needed
  - [x] 5.3: Add `scripts/` directory reference to `Makefile` — add `make build-index` target: `python backend/scripts/build_faiss_index.py`

- [x] Task 6: Manual verification (AC: #1-#5)
  - [x] 6.1: Run `python backend/scripts/build_faiss_index.py` — confirm output files exist
  - [x] 6.2: Inspect `index_metadata.json` — verify all 6 knowledge documents are represented
  - [x] 6.3: Run a manual Python snippet to test a sample query (see Dev Notes below)
  - [x] 6.4: Check index file sizes — `du -sh backend/data/faiss_index/` should be well under 50MB
  - [x] 6.5: Run `pytest backend/tests/test_faiss_index.py -v` — all tests pass

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow these exactly:**

- **Embedding model is `all-MiniLM-L6-v2`** — this is the architecture decision (ADR in architecture.md). Do NOT use a different model. It produces 384-dim embeddings. Already in `requirements.txt` as `sentence-transformers`. Model downloads ~80MB on first use.
- **FAISS index type is `IndexFlatIP`** — not `IndexFlatL2`. Normalize embeddings first (`faiss.normalize_L2(emb)`), then inner product = cosine similarity. This is the correct approach for semantic search.
- **Knowledge files location: `backend/data/knowledge/`** — per architecture project structure. NOT in `backend/scripts/`, NOT in project root.
- **FAISS index output: `backend/data/faiss_index/`** — this is the `FAISS_INDEX_PATH` default in `config.py`. Lambda reads from this path locally; S3 path is used in production.
- **`index_metadata.json` is the chunk-to-source mapping** — vector index position N in FAISS = metadata list position N. This mapping is CRITICAL for citation attribution in Story 3.2.
- **`faiss-cpu` is already in `requirements.txt`** — do NOT add it again.
- **`sentence-transformers` is already in `requirements.txt`** — do NOT add it again.
- **`anthropic` is already in `requirements.txt`** — not used in this story but present.

### config.py Integration

`FAISS_INDEX_PATH` is already defined in `backend/config.py`:
```python
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
```

The build script should save to the hardcoded path `backend/data/faiss_index/` (repo-relative). The `rag_service.py` in Story 3.2 will use `config.FAISS_INDEX_PATH` to load it.

### Lambda FAISS Loading Pattern (for Story 3.2 context)

On Lambda cold start, the RAG service will:
```python
import boto3, faiss, json, os
from config import FAISS_INDEX_PATH, S3_BUCKET

# On Lambda, FAISS_INDEX_PATH = "/tmp/faiss_index"
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
s3 = boto3.client("s3")
s3.download_file(S3_BUCKET, "faiss_index/index.faiss", f"{FAISS_INDEX_PATH}/index.faiss")
s3.download_file(S3_BUCKET, "faiss_index/index_metadata.json", f"{FAISS_INDEX_PATH}/index_metadata.json")
index = faiss.read_index(f"{FAISS_INDEX_PATH}/index.faiss")
with open(f"{FAISS_INDEX_PATH}/index_metadata.json") as f:
    metadata = json.load(f)
```

This story does NOT implement the Lambda loading — that is Story 3.2. But the index format must be compatible.

### Manual Verification Snippet

Run this after building the index to verify it works end-to-end:
```python
import faiss, json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("backend/data/faiss_index/index.faiss")
with open("backend/data/faiss_index/index_metadata.json") as f:
    metadata = json.load(f)

query = "progressive overload periodization principles"
emb = model.encode([query])
faiss.normalize_L2(emb)
distances, indices = index.search(emb, k=3)

for i, idx in enumerate(indices[0]):
    print(f"[{i+1}] Score: {distances[0][i]:.3f}")
    print(f"     Source: {metadata[idx]['source']}")
    print(f"     Principle: {metadata[idx]['principle']}")
    print(f"     Text: {metadata[idx]['text'][:100]}...")
```

### Chunking Implementation Detail

```python
import re
from pathlib import Path

def chunk_document(filepath: Path) -> list[dict]:
    text = filepath.read_text()
    sections = re.split(r'\n(?=## )', text)
    chunks = []
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
        header = lines[0].replace('## ', '').strip() if lines[0].startswith('##') else filepath.stem
        body = '\n'.join(lines[1:]).strip()
        # Split long sections at paragraph breaks
        paragraphs = [p.strip() for p in body.split('\n\n') if len(p.strip()) >= 50]
        if not paragraphs:
            if len(body) >= 50:
                paragraphs = [body]
            else:
                continue
        for para in paragraphs:
            chunks.append({
                "source": filepath.name,
                "principle": header,
                "text": para
            })
    return chunks
```

### Knowledge Content Requirements

Each knowledge document must cover enough breadth to be useful for coaching queries. Minimum expectations:

| Document | Key Topics Required |
|----------|---------------------|
| `periodization.md` | Linear, DUP, block, peaking, taper protocols |
| `progressive_overload.md` | SRA curve, Prilepin's Chart, fatigue management, load progression |
| `powerlifting.md` | Squat/bench/deadlift technique cues, frequency, competition prep, openers |
| `grip_sport.md` | Gripper progression (closes, negatives), hub lift training, event specificity, competition strategy |
| `armwrestling.md` | Pronation, supination, side pressure, hook mechanics, table-time importance, conditioning |
| `cross_domain.md` | How max strength base transfers, tendon timeline (6-12 weeks), adaptation specificity principle |

Write from the perspective of evidence-based coaching. Use concrete numbers where available (e.g., "2-3 sessions/week for strength development"). Each doc should be readable and internally coherent — the LLM will receive these chunks verbatim as context.

### File Structure

Files this story creates:
```
backend/
├── data/
│   ├── knowledge/                    # NEW directory
│   │   ├── periodization.md          # NEW
│   │   ├── progressive_overload.md   # NEW
│   │   ├── powerlifting.md           # NEW
│   │   ├── grip_sport.md             # NEW
│   │   ├── armwrestling.md           # NEW
│   │   └── cross_domain.md           # NEW
│   └── faiss_index/                  # NEW directory (generated output)
│       ├── index.faiss               # GENERATED by build script
│       └── index_metadata.json       # GENERATED by build script
├── scripts/                          # NEW directory
│   ├── build_faiss_index.py          # NEW
│   └── upload_index_to_s3.py         # NEW
└── tests/
    └── test_faiss_index.py           # NEW
```

Files NOT created or modified:
- `backend/requirements.txt` — already has `faiss-cpu`, `sentence-transformers`
- `backend/config.py` — `FAISS_INDEX_PATH` already defined
- `backend/main.py` — no new router needed (this is an operator script story, not an API endpoint)
- No frontend changes — this story has zero frontend work
- No DynamoDB changes — FAISS index is a file on disk/S3

**Add to `.gitignore`:** `backend/data/faiss_index/` (generated files, large binary) — add if not already ignored.

### Testing Requirements

- `test_faiss_index.py` tests require the index to be built first. Mark with `@pytest.mark.requires_index`.
- In `conftest.py`, add: `pytest.ini_options = {"markers": ["requires_index: requires FAISS index to be built"]}` and skip if files don't exist.
- Existing tests (`test_sessions.py`, `test_exercises.py`, etc.) must continue to pass — no changes to existing test infrastructure.
- Run with: `pytest backend/tests/ -v` — all 22+ existing tests still pass; new FAISS tests added.

### Previous Story Intelligence (Stories 2.1-2.3)

- `backend/services/` pattern: `session_service.py`, `exercise_service.py` already present. The `rag_service.py` (Story 3.2) will follow the same service pattern and will load the FAISS index you build here.
- `backend/data/exercises.json` is the established pattern for static data files loaded at startup — the FAISS index follows the same "data bundled with backend" pattern for local dev.
- `conftest.py` fixtures: `test_client`, `dynamodb_mock`, `test_user_id` already set up. Your FAISS tests don't need DynamoDB — just filesystem reads.
- All existing backend tests use `moto` for DynamoDB mocking. **Do NOT add moto to FAISS tests** — completely different domain.
- Commit pattern: simple descriptive message like "completed story 3-1" — no conventional commits needed.

### Anti-Patterns to Avoid

- **DO NOT** use `IndexFlatL2` — use `IndexFlatIP` with normalized vectors (cosine similarity is better for semantic search).
- **DO NOT** use HuggingFace embeddings API — use local `SentenceTransformer("all-MiniLM-L6-v2")` (free, local, no API key).
- **DO NOT** create a new FastAPI endpoint for querying the index in this story — that is Story 3.2 (`POST /query` with full RAG pipeline).
- **DO NOT** store chunks in DynamoDB — FAISS index is a binary file on disk/S3, metadata is a JSON sidecar file.
- **DO NOT** use `IndexIVFFlat` or quantized indexes — the corpus is small (< 500 chunks), flat index is both simpler and sufficient.
- **DO NOT** add FAISS index files to git — they are generated artifacts (`backend/data/faiss_index/` should be gitignored).
- **DO NOT** load the FAISS index in `main.py` startup — that belongs in `rag_service.py` (Story 3.2). This story is scripts only.
- **DO NOT** create a `/index` API endpoint or similar — the FAISS index is not user-facing.

### References

- [Source: epics.md#Story 3.1] — Acceptance criteria, FR24, FR26, NFR16, script paths
- [Source: architecture.md#Data Architecture] — `all-MiniLM-L6-v2`, 384-dim embeddings, FAISS index on S3, `index_metadata.json` chunk-to-source mapping
- [Source: architecture.md#Infrastructure & Deployment] — `FAISS_INDEX_PATH` env var, S3 index storage, Lambda cold start download pattern
- [Source: architecture.md#Project Structure] — `backend/data/faiss_index/`, `backend/scripts/build_faiss_index.py`, `backend/scripts/upload_index_to_s3.py`
- [Source: architecture.md#Requirements] — Additional requirements: `sentence-transformers (all-MiniLM-L6-v2)`, `faiss-cpu`, `FAISS_INDEX_PATH` config
- [Source: architecture.md#Service Boundaries] — `rag_service` will consume the index built here; `rag_service` calls `session_service.get_user_sessions()` for personal data
- [Source: architecture.md#Data Flow] — AI Coaching Flow: embed query → FAISS search → DynamoDB fetch → Claude API call
- [Source: implementation-artifacts/2-3-session-history-detail-view.md#Dev Notes] — `conftest.py` test fixture patterns, moto DynamoDB mock pattern, existing test count (22 tests), commit pattern
- [Source: architecture.md#Format Patterns] — `index_metadata.json` structure: `{ source, principle, text }` per chunk — matches AI response citation format
- [Source: architecture.md#Environment Config] — `FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")` already in config.py

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation completed without blockers.

### Completion Notes List

- Created 6 knowledge base markdown documents covering all required domains (periodization, progressive overload, powerlifting, grip sport, armwrestling, cross-domain transfer). Each doc is 400-700 words with `##` section headers enabling clean paragraph-level chunking.
- `build_faiss_index.py` chunks all documents at `##` headers, then splits large sections at paragraph breaks (min 50 chars). Produces 68 chunks from 6 files. Uses `IndexFlatIP` with L2-normalized embeddings (cosine similarity). Total index size: 132 KB — well under 50 MB AC#3.
- `upload_index_to_s3.py` reads `S3_BUCKET` env var, uploads both files to `faiss_index/` S3 prefix using boto3.
- `conftest.py` updated with `requires_index` marker and auto-skip logic if index files are absent (prevents CI failures before index is built).
- 5 new FAISS tests added. All 27 tests (22 existing + 5 new) pass. Zero regressions.
- `make build-index` target added to Makefile. `backend/data/faiss_index/` added to `.gitignore`.

### File List

- `backend/data/knowledge/periodization.md` — NEW
- `backend/data/knowledge/progressive_overload.md` — NEW
- `backend/data/knowledge/powerlifting.md` — NEW
- `backend/data/knowledge/grip_sport.md` — NEW
- `backend/data/knowledge/armwrestling.md` — NEW
- `backend/data/knowledge/cross_domain.md` — NEW
- `backend/scripts/build_faiss_index.py` — NEW
- `backend/scripts/upload_index_to_s3.py` — NEW
- `backend/tests/test_faiss_index.py` — NEW
- `backend/tests/conftest.py` — MODIFIED (added requires_index marker + skip logic)
- `Makefile` — MODIFIED (added build-index target)
- `.gitignore` — MODIFIED (added backend/data/faiss_index/)

### Change Log

- 2026-04-25: Implemented Story 3.1 — knowledge base ingestion and FAISS index. Created 6 domain knowledge documents, build/upload scripts, pytest tests. All 27 tests pass. Index: 68 chunks, 132 KB.
