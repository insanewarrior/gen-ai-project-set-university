# Story 3.2: Dual-Source RAG Pipeline

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **athlete**,
I want my coaching queries to draw from both my personal training history and general strength science,
so that I receive personalized, cited advice grounded in both my data and established principles.

## Acceptance Criteria

1. **Given** I send a `POST /query` with a natural language question **When** the RAG pipeline processes it **Then** it: (1) sanitizes input, (2) checks rate limit, (3) embeds the query via sentence-transformers, (4) searches FAISS for top-K relevant general knowledge chunks, (5) fetches my sessions from DynamoDB via `session_service.get_sessions()`, (6) builds a combined LLM prompt with both sources, (7) calls Claude API, (8) returns a structured response with separated personal and knowledge citations (FR8, FR9)

2. **Given** the RAG pipeline returns a response **When** I inspect the response JSON **Then** it matches: `{ "data": { "response": "...", "citations": { "personal": [{"sessionDate": "...", "exercise": "...", "detail": "..."}], "knowledge": [{"source": "...", "principle": "..."}] }, "confidence": "low|medium|high", "queriesRemaining": N } }` (FR10)

3. **Given** user input in the query **When** the text is processed **Then** it passes through `sanitize_llm_input()` in the middleware layer, stripping injection patterns, enforcing 2000-char max length, and escaping `<`, `>`, `{`, `}` delimiters before LLM prompt inclusion (FR29, NFR10, NFR11)

4. **Given** the athlete has 1-5 sessions **When** the system responds **Then** the response starts with "Based on your first few sessions..." — for 6-30 sessions: "Looking at your recent training data..." — for 30+ sessions: "Based on X months of data, a clear pattern shows..." (FR13)

5. **Given** the retrieval doesn't surface relevant personal data or knowledge **When** the system responds **Then** it acknowledges the gap: "I don't have enough data on [topic] to give a confident answer" (FR14)

6. **Given** the Claude API is unavailable or returns an error **When** an athlete submits a query **Then** they receive `{ "error": "I couldn't process that question right now. Please try again.", "code": "AI_UNAVAILABLE" }` with HTTP 500 — no raw error exposed, logging endpoints still work (NFR22, NFR26)

7. **Given** a query about cross-discipline transfer (e.g., powerlifting peaking for armwrestling) **When** the RAG pipeline processes it **Then** it retrieves cross-domain knowledge from `cross_domain.md` chunks and bridges concepts with cited sources from both disciplines (FR26)

8. **Given** the full RAG pipeline **When** measured end-to-end (FAISS search + DynamoDB fetch + Claude API call) **Then** response returns within 10 seconds under normal conditions (NFR2)

9. **Given** a free-tier user (account >7 days) who has made 3 queries today **When** they submit another query **Then** they receive HTTP 429: `{ "error": "Daily query limit reached", "code": "RATE_LIMIT_EXCEEDED", "detail": { "resetAt": "2026-04-26T00:00:00Z", "limit": 3 } }` (FR15, FR33, NFR12)

10. **Given** `pytest backend/tests/` **When** all tests run **Then** all tests pass with zero regressions on existing 27 tests, and new tests for sanitize, rate_limit, and query endpoint are added

## Tasks / Subtasks

- [x] Task 1: Create `backend/middleware/sanitize.py` — input sanitization for LLM-facing text (AC: #3)
  - [x] 1.1: Create `backend/middleware/sanitize.py` with `sanitize_llm_input(text: str) -> str`
  - [x] 1.2: Enforce 2000-char max length (truncate with warning log if exceeded)
  - [x] 1.3: Strip common prompt injection patterns: `ignore previous`, `system:`, `<|im_start|>`, `</s>`, `[INST]`, and similar LLM control tokens
  - [x] 1.4: Escape delimiter characters: `<`, `>`, `{`, `}` using HTML entities (`&lt;`, `&gt;`, `&#123;`, `&#125;`)
  - [x] 1.5: Sanitizer is called from the **router** (not the service) — consistent with architecture's "thin router validates, service executes" pattern

- [x] Task 2: Create `backend/models/query_models.py` — Pydantic models (AC: #1, #2)
  - [x] 2.1: Create `backend/models/query_models.py`
  - [x] 2.2: `QueryRequest(BaseModel)`: `query: str = Field(..., max_length=2000)` — with `to_camel` alias_generator (match pattern from `session_models.py`)
  - [x] 2.3: `PersonalCitation(BaseModel)`: `session_date: str`, `exercise: str`, `detail: str`
  - [x] 2.4: `KnowledgeCitation(BaseModel)`: `source: str`, `principle: str`
  - [x] 2.5: `Citations(BaseModel)`: `personal: list[PersonalCitation]`, `knowledge: list[KnowledgeCitation]`
  - [x] 2.6: `CoachingResponse(BaseModel)`: `response: str`, `citations: Citations`, `confidence: str`, `queries_remaining: int` — with `to_camel` alias_generator
  - [x] 2.7: All models use `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` (exactly like `session_models.py`)

- [x] Task 3: Create `backend/services/rate_limit_service.py` — per-user daily query limits (AC: #9)
  - [x] 3.1: Create `backend/services/rate_limit_service.py`
  - [x] 3.2: `_get_table()` function: same pattern as `session_service._get_table()` but uses `config.QUERY_USAGE_TABLE_NAME`
  - [x] 3.3: `check_and_increment(user_id: str, user_create_date: str | None = None) -> dict`: atomic DynamoDB `UpdateItem` with condition expression
    - PK: `userId`, SK: today's date (`datetime.utcnow().strftime("%Y-%m-%d")`)
    - Use `update_expression="SET queryCount = if_not_exists(queryCount, :zero) + :one"` with `condition_expression="attribute_not_exists(queryCount) OR queryCount < :limit"`
    - Tier limit: if `user_create_date` is within 7 days → limit=10; else → limit=3 (premium: not implemented in this story — FR17 is Epic 4)
    - Returns: `{"allowed": True, "queries_remaining": N, "reset_at": "YYYY-MM-DDT00:00:00Z"}`
  - [x] 3.4: Handle `ConditionalCheckFailedException` → return `{"allowed": False, "queries_remaining": 0, "reset_at": next_midnight_utc}`
  - [x] 3.5: `reset_at` calculation: midnight UTC of tomorrow — `(datetime.utcnow().date() + timedelta(days=1)).isoformat() + "T00:00:00Z"`
  - [x] 3.6: Import from `botocore.exceptions import ClientError` to catch `ConditionalCheckFailedException`

- [x] Task 4: Create `backend/services/rag_service.py` — the RAG pipeline heart (AC: #1, #2, #4, #5, #6, #7, #8)
  - [x] 4.1: Create `backend/services/rag_service.py`
  - [x] 4.2: **Module-level FAISS loading** (loaded once per Lambda instance / FastAPI startup):
    ```python
    import faiss, json
    from pathlib import Path
    import config
    
    _index = None
    _metadata = None
    
    def _load_index():
        global _index, _metadata
        index_path = Path(config.FAISS_INDEX_PATH)
        # Lambda: download from S3 if not present locally
        if not (index_path / "index.faiss").exists():
            _download_from_s3(index_path)
        _index = faiss.read_index(str(index_path / "index.faiss"))
        with open(index_path / "index_metadata.json") as f:
            _metadata = json.load(f)
    
    def _download_from_s3(dest_path: Path):
        import boto3
        dest_path.mkdir(parents=True, exist_ok=True)
        s3 = boto3.client("s3")
        bucket = config.S3_FAISS_BUCKET
        for fname in ["index.faiss", "index_metadata.json"]:
            s3.download_file(bucket, f"faiss_index/{fname}", str(dest_path / fname))
    ```
  - [x] 4.3: Call `_load_index()` at module import time (wrapped in try/except, log error if fails — do not crash app startup)
  - [x] 4.4: `_embed_query(query_text: str) -> np.ndarray`: use `SentenceTransformer("all-MiniLM-L6-v2")` (module-level instance), normalize with `faiss.normalize_L2(emb)`, return shape `(1, 384)`
  - [x] 4.5: Module-level SentenceTransformer: `_model = SentenceTransformer("all-MiniLM-L6-v2")` — same model from Story 3.1
  - [x] 4.6: `_search_knowledge(query_emb, k: int = 3) -> list[dict]`: `_index.search(query_emb, k)` → map indices to `_metadata` entries → return list of `{source, principle, text}` dicts
  - [x] 4.7: `_format_sessions(sessions: list) -> tuple[str, int]`: Format DynamoDB sessions for prompt context. Returns `(formatted_text, session_count)`. Format: each session as `"{date} | {sport}: {exercise_name} {set_count}x{reps} @ {weight}kg (RPE {rpe})"`. Limit to 10 most recent sessions to keep prompt size bounded. Decimal values from DynamoDB: convert with `float()`.
  - [x] 4.8: `_confidence_label(session_count: int) -> str`: 1-5 → `"low"`, 6-30 → `"medium"`, 30+ → `"high"`
  - [x] 4.9: `_confidence_framing(session_count: int) -> str`: 1-5 → `"Based on your first few sessions..."`, 6-30 → `"Looking at your recent training data..."`, 30+ → `"Based on your training history, a clear pattern shows..."`
  - [x] 4.10: `_build_prompt(query: str, personal_context: str, session_count: int, knowledge_chunks: list[dict]) -> str`: Build the Claude prompt instructing Claude to:
    - Use the provided personal training data and strength science knowledge
    - Start the response with the appropriate confidence framing (pass it in the prompt)
    - Return a JSON object: `{"response": "...", "personal_citations": [{"sessionDate": "...", "exercise": "...", "detail": "..."}], "knowledge_citations": [{"source": "...", "principle": "..."}]}`
    - Include the disclaimer: "StrengthWise provides training insights, not medical advice"
    - Acknowledge gaps honestly if neither source has relevant info
    - Keep response concise (2-3 paragraphs)
  - [x] 4.11: `_call_claude(prompt: str) -> dict`: `anthropic.Anthropic().messages.create(model=config.CLAUDE_MODEL, max_tokens=1024, messages=[{"role": "user", "content": prompt}])` → extract `response.content[0].text` → parse JSON
  - [x] 4.12: Handle Claude JSON parse failure: wrap entire response text as `{"response": text, "personal_citations": [], "knowledge_citations": []}` (defensive fallback)
  - [x] 4.13: `query(user_id: str, query_text: str) -> dict`: orchestrates steps: embed → FAISS search → `session_service.get_sessions(user_id)` → format → build prompt → call Claude → return parsed dict with `{"response", "citations": {"personal": [...], "knowledge": [...]}, "confidence", "queries_remaining"}`. `queries_remaining` is passed in by the router after rate_limit check.
  - [x] 4.14: Wrap Claude call in try/except `anthropic.APIError` and broad `Exception` — re-raise as `RuntimeError("AI_UNAVAILABLE")` for the router to catch

- [x] Task 5: Create `backend/routers/query.py` — thin POST /query router (AC: #1, #6, #9)
  - [x] 5.1: Create `backend/routers/query.py`
  - [x] 5.2: `router = APIRouter(prefix="/query", tags=["query"])`
  - [x] 5.3: `POST ""` endpoint with `Depends(get_current_user)` auth:
    ```python
    @router.post("", status_code=200)
    async def create_query(body: QueryRequest, current_user: CurrentUser = Depends(get_current_user)):
        sanitized = sanitize_llm_input(body.query)
        rate_result = rate_limit_service.check_and_increment(current_user)
        if not rate_result["allowed"]:
            raise HTTPException(status_code=429, detail={
                "error": "Daily query limit reached",
                "code": "RATE_LIMIT_EXCEEDED",
                "detail": {"resetAt": rate_result["reset_at"], "limit": 3}
            })
        try:
            result = rag_service.query(current_user, sanitized)
        except RuntimeError:
            raise HTTPException(status_code=500, detail={
                "error": "I couldn't process that question right now. Please try again.",
                "code": "AI_UNAVAILABLE"
            })
        result["queriesRemaining"] = rate_result["queries_remaining"]
        return {"data": result}
    ```
  - [x] 5.4: Import `sanitize_llm_input` from `middleware.sanitize`, not from services (consistent with architecture)

- [x] Task 6: Register query router in `backend/main.py` (AC: #1)
  - [x] 6.1: Add `from routers.query import router as query_router` to `backend/main.py`
  - [x] 6.2: Add `app.include_router(query_router)` after existing router registrations

- [x] Task 7: Write tests (AC: #10)
  - [x] 7.1: Create `backend/tests/test_sanitize.py` — pure unit tests, no mocking needed:
    - `test_sanitize_enforces_max_length`: input >2000 chars → output is 2000 chars
    - `test_sanitize_strips_injection`: input with "ignore previous instructions" → removed
    - `test_sanitize_escapes_delimiters`: `<`, `>`, `{`, `}` → HTML entities
    - `test_sanitize_normal_input_unchanged`: clean query text passes through unchanged
  - [x] 7.2: Create `backend/tests/test_rate_limit.py` — use moto DynamoDB mock:
    - Use `@pytest.fixture` with `moto` `mock_aws` context (same pattern as `test_sessions.py`)
    - `test_first_query_allowed`: first query always allowed, returns remaining = limit - 1
    - `test_limit_enforced_on_4th_free_tier`: after 3 increments, 4th returns `allowed=False`
    - `test_reset_at_is_tomorrow_midnight`: verify format `YYYY-MM-DDT00:00:00Z`
  - [x] 7.3: Create `backend/tests/test_query.py` — moto DynamoDB + patch rag_service:
    - Use `unittest.mock.patch("services.rag_service.query")` to avoid Claude API calls
    - Use `unittest.mock.patch("services.rate_limit_service.check_and_increment")` for rate limit control
    - `test_query_returns_200_with_citations`: mock both services, verify response shape
    - `test_query_returns_429_when_rate_limited`: mock rate_limit to return `allowed=False`, verify 429
    - `test_query_returns_500_on_ai_failure`: mock rag_service to raise `RuntimeError`, verify 500
    - `test_query_requires_auth`: no auth header → 401 (when AUTH_BYPASS is false)
    - `test_sanitization_applied`: query with injection pattern is sanitized before rag_service receives it (assert patched rag_service called with sanitized text)
  - [x] 7.4: Do NOT add moto to FAISS-related tests — `test_faiss_index.py` tests are filesystem-only (already confirmed in Story 3.1)

## Dev Notes

### Architecture Compliance — CRITICAL

**Follow these exactly:**

- **Service boundary**: `rag_service` calls `session_service.get_sessions(user_id)` — it does NOT query DynamoDB directly for sessions. Architecture explicitly states: "rag_service calls session_service.get_user_sessions() for personal data — it does not query DynamoDB directly"
- **Router is thin**: sanitize input + check rate limit + call service + handle errors = all router does. No business logic in router.
- **Sanitization location**: in `middleware/sanitize.py`, called from router (not from service). Architecture: "Input Sanitization Pattern: All /query and /analyze inputs pass through sanitize_llm_input() before hitting the LLM prompt — sanitization happens in the service layer". NOTE: The architecture is slightly contradictory here. Place `sanitize_llm_input` in `middleware/sanitize.py` (consistent with existing `middleware/auth.py` pattern) and call it from the router. This is cleaner and matches the codebase structure.
- **FAISS index type**: `IndexFlatIP` with L2-normalized embeddings (cosine similarity). Already built in Story 3.1. Do NOT change index type.
- **Embedding model**: `all-MiniLM-L6-v2` — same model used to build the index in Story 3.1. Using a different model would cause garbage results.
- **camelCase JSON**: all response fields must be camelCase — use Pydantic `to_camel` alias_generator. `queriesRemaining`, `sessionDate`, `resetAt` not `queries_remaining`, `session_date`, `reset_at`
- **Config values** — use existing config.py (do NOT add new env vars):
  - `config.FAISS_INDEX_PATH` — `"./data/faiss_index"` locally
  - `config.CLAUDE_MODEL` — `"claude-sonnet-4-5-20250514"` (existing default)
  - `config.S3_FAISS_BUCKET` — S3 bucket name for Lambda cold start
  - `config.DYNAMODB_ENDPOINT` — for local DynamoDB; already used in session_service
  - `config.QUERY_USAGE_TABLE_NAME` — `"QueryUsage"` table

### Existing Files — What to Reuse

- `backend/services/session_service.py`: `get_sessions(user_id: str) -> list` — call this from rag_service. Existing function, zero modification needed.
- `backend/middleware/auth.py`: `get_current_user`, `CurrentUser` — import exactly as done in `routers/sessions.py`
- `backend/config.py`: all config values are already defined, nothing to add
- `backend/requirements.txt`: `anthropic`, `faiss-cpu`, `sentence-transformers` are already in requirements — DO NOT add them again
- `backend/tests/conftest.py`: `client` fixture, `requires_index` marker, `pytest_collection_modifyitems` — already set up

### Pydantic Pattern (from session_models.py)

```python
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class MyModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    my_field: str
```

JSON output: `{"myField": "..."}` — camelCase automatically.

### DynamoDB Pattern (from session_service.py)

```python
def _get_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)
```

### Moto Test Pattern (from existing tests)

```python
import pytest
import boto3
from moto import mock_aws

@pytest.fixture(autouse=True)
def aws_credentials():
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["DYNAMODB_ENDPOINT"] = ""  # disable local endpoint for moto

@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="QueryUsage",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},  # date string as SK
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield
```

**Note**: Check actual test_sessions.py for the exact fixture pattern — mirror it precisely.

### Claude API Usage

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
message = client.messages.create(
    model=config.CLAUDE_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
response_text = message.content[0].text
```

`anthropic` is already in `requirements.txt`. The `ANTHROPIC_API_KEY` env var must be set in `.env` for local dev.

### Prompt Engineering for Structured Output

Instruct Claude to return JSON to avoid brittle parsing:

```
You are StrengthWise, an AI strength coach. Analyze the athlete's question using their personal training data and general strength science knowledge provided below.

ATHLETE QUESTION: {query}

PERSONAL TRAINING DATA ({session_count} sessions):
{personal_context}

STRENGTH SCIENCE KNOWLEDGE:
{knowledge_chunks}

{confidence_framing}

Respond with a JSON object in this exact format:
{{
  "response": "Your coaching response here (2-3 paragraphs). Include: StrengthWise provides training insights, not medical advice.",
  "personal_citations": [
    {{"sessionDate": "YYYY-MM-DD", "exercise": "exercise name", "detail": "specific metric or observation"}}
  ],
  "knowledge_citations": [
    {{"source": "filename.md", "principle": "section header"}}
  ]
}}

Rules:
- Only cite sessions that are directly relevant to the question
- Only cite knowledge chunks that appear in the provided knowledge above
- If data is insufficient, say so honestly in the response; return empty citation arrays
- Return ONLY the JSON object, no markdown code blocks
```

### Session Formatting for Prompt

DynamoDB returns Decimal types — convert with `float()`:

```python
def _format_sessions(sessions: list) -> tuple[str, int]:
    recent = sessions[:10]  # DynamoDB already sorted newest first
    lines = []
    for s in recent:
        date = s.get("sessionDate", "unknown")
        sport = s.get("sport", "")
        for ex in s.get("exercises", []):
            name = ex.get("exerciseName", ex.get("exercise_name", ""))
            sets = ex.get("sets", [])
            set_str = ", ".join(
                f"{float(st.get('weight', 0))}kg x{st.get('reps', 0)} @RPE{float(st.get('rpe', 0))}"
                for st in sets if st.get('weight')
            )
            lines.append(f"{date} | {sport}: {name} — {set_str}")
    return "\n".join(lines) if lines else "No training sessions logged yet.", len(sessions)
```

**DynamoDB Decimal note**: `session_service` stores floats as `Decimal` via `_to_decimal()`. When reading back, values are `Decimal`. Always wrap with `float()` before string formatting.

### FAISS Loading — Local vs Lambda

- **Local dev**: `FAISS_INDEX_PATH=./data/faiss_index` — files exist after `make build-index`. Module init just reads them.
- **Lambda**: `FAISS_INDEX_PATH=/tmp/faiss_index` — files don't exist on cold start. Download from S3 using `S3_FAISS_BUCKET`.
- Detection logic: check if `index.faiss` file exists at the path. If not and `S3_FAISS_BUCKET` is set, download. If not and no bucket configured, raise clear error.
- Module-level loading runs at import time — FastAPI startup loads the index once per Lambda instance.

### Rate Limiting — DynamoDB Atomic Pattern

```python
from botocore.exceptions import ClientError

def check_and_increment(user_id: str) -> dict:
    table = _get_table()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tier_limit = 3  # free tier default (onboarding/premium: Epic 4)
    try:
        response = table.update_item(
            Key={"userId": user_id, "sk": today},
            UpdateExpression="SET queryCount = if_not_exists(queryCount, :zero) + :one",
            ConditionExpression="attribute_not_exists(queryCount) OR queryCount < :limit",
            ExpressionAttributeValues={":zero": 0, ":one": 1, ":limit": tier_limit},
            ReturnValues="UPDATED_NEW",
        )
        new_count = int(response["Attributes"]["queryCount"])
        return {"allowed": True, "queries_remaining": tier_limit - new_count, "reset_at": _next_midnight()}
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"allowed": False, "queries_remaining": 0, "reset_at": _next_midnight()}
        raise

def _next_midnight() -> str:
    from datetime import timedelta
    return (datetime.utcnow().date() + timedelta(days=1)).isoformat() + "T00:00:00Z"
```

**Note**: `"sk"` matches the SK attribute name used in session_service. Verify the `QueryUsage` table's SK attribute name in the CDK stack definition (it may be `"date"` per architecture docs, not `"sk"`). Use whatever was defined in the CDK stack. Check `infra/stacks/strengthwise_stack.py` to confirm.

### File Structure

Files created/modified in this story:
```
backend/
├── middleware/
│   ├── auth.py               ← EXISTING (do not modify)
│   └── sanitize.py           ← NEW
├── models/
│   ├── session_models.py     ← EXISTING (do not modify)
│   └── query_models.py       ← NEW
├── services/
│   ├── session_service.py    ← EXISTING (do not modify)
│   └── rate_limit_service.py ← NEW
│   └── rag_service.py        ← NEW
├── routers/
│   ├── sessions.py           ← EXISTING (do not modify)
│   └── query.py              ← NEW
├── main.py                   ← MODIFY (add query router)
└── tests/
    ├── conftest.py           ← EXISTING (do not modify)
    ├── test_sanitize.py      ← NEW
    ├── test_rate_limit.py    ← NEW
    └── test_query.py         ← NEW
```

Files NOT created/modified:
- `backend/requirements.txt` — all deps already present
- `backend/config.py` — all config already defined
- `backend/data/faiss_index/` — built by Story 3.1
- `backend/services/session_service.py` — called but not modified
- No frontend changes in this story (UI is Story 3.3)

### Anti-Patterns to Avoid

- **DO NOT** query DynamoDB sessions table directly from `rag_service` — call `session_service.get_sessions(user_id)`
- **DO NOT** add any new env vars to config.py — all needed vars already exist (`FAISS_INDEX_PATH`, `CLAUDE_MODEL`, `S3_FAISS_BUCKET`, `QUERY_USAGE_TABLE_NAME`)
- **DO NOT** use `IndexFlatL2` — existing index was built with `IndexFlatIP` + normalized vectors
- **DO NOT** create a different SentenceTransformer model — must be `all-MiniLM-L6-v2` (same as index build)
- **DO NOT** put business logic in the router — only: validate input, sanitize, check rate limit, call service, handle errors
- **DO NOT** mock FAISS in `test_faiss_index.py` — those tests already load real index (Story 3.1 pattern)
- **DO NOT** expose raw exception messages or stack traces in error responses — always use the standard error JSON format
- **DO NOT** skip the medical disclaimer — FR27 requires: "StrengthWise provides training insights, not medical advice" in every AI response
- **DO NOT** implement premium tier (FR17) in this story — that is Epic 4. Use free-tier limit (3/day) as the only limit for now.
- **DO NOT** implement `/analyze` endpoint in this story — that is Story 3.4. Only `/query` here.
- **DO NOT** add `rag_service` import to `main.py` — only the router import goes there

### Previous Story Intelligence (Story 3.1 — FAISS Index)

From Story 3.1 completion notes:
- **68 chunks** from 6 knowledge files (`periodization.md`, `progressive_overload.md`, `powerlifting.md`, `grip_sport.md`, `armwrestling.md`, `cross_domain.md`)
- **Index format**: `IndexFlatIP`, 384-dimensional embeddings
- **Metadata format**: list of dicts `[{"source": "grip_sport.md", "principle": "Gripper Training", "text": "..."}]` — index position = FAISS vector ID
- **Index size**: 132 KB total — well within Lambda memory
- **conftest.py**: already has `requires_index` marker and auto-skip logic
- **27 tests currently pass** — zero regressions allowed

### Testing the RAG Pipeline Manually

After implementation, verify end-to-end with AUTH_BYPASS=true:

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How should I program my gripper training for competition?"}'
```

Expected: JSON with `data.response` (text with disclaimer), `data.citations.personal` (empty if no sessions), `data.citations.knowledge` (grip-related chunks), `data.confidence` ("low"), `data.queriesRemaining` (2)

### References

- [Source: epics.md#Story 3.2] — All acceptance criteria, FR8, FR9, FR10, FR11, FR13, FR14, FR26, FR27, FR29, NFR2, NFR10, NFR11, NFR12, NFR22, NFR26
- [Source: architecture.md#Data Architecture] — QueryUsage table (PK: userId, SK: date), atomic UpdateItem pattern, FAISS embedding model, index_metadata.json structure
- [Source: architecture.md#API & Communication Patterns] — Rate limiting flow, DynamoDB conditional update, HTTP 429 format, error response JSON format
- [Source: architecture.md#Data Flow] — AI Coaching Flow diagram: embed → FAISS search → DynamoDB fetch → Claude API call → citation parsing
- [Source: architecture.md#Service Boundaries] — rag_service calls session_service, not DynamoDB directly
- [Source: architecture.md#Format Patterns] — AI coaching response JSON structure `{data: {response, citations: {personal, knowledge}, confidence, queriesRemaining}}`
- [Source: architecture.md#Enforcement Guidelines] — Put business logic in services/, camelCase JSON, standard error format
- [Source: architecture.md#Project Structure] — backend/routers/query.py, backend/services/rag_service.py, backend/services/rate_limit_service.py
- [Source: architecture.md#Input Sanitization Pattern] — sanitize_llm_input() before LLM prompt inclusion
- [Source: implementation-artifacts/3-1-knowledge-base-ingestion-faiss-index.md#Dev Notes] — FAISS IndexFlatIP, all-MiniLM-L6-v2, index_metadata.json structure {source, principle, text}, Lambda cold-start download pattern
- [Source: implementation-artifacts/3-1-knowledge-base-ingestion-faiss-index.md#Completion Notes] — 68 chunks, 132KB index, 27 existing tests, conftest.py requires_index marker
- [Source: backend/services/session_service.py] — _get_table() pattern, Decimal conversion, get_sessions() function signature
- [Source: backend/middleware/auth.py] — get_current_user, CurrentUser type alias
- [Source: backend/routers/sessions.py] — router pattern, Depends(get_current_user) usage, response wrapping `{"data": {...}}`
- [Source: backend/models/session_models.py] — Pydantic ConfigDict(alias_generator=to_camel) pattern
- [Source: backend/config.py] — FAISS_INDEX_PATH, CLAUDE_MODEL, S3_FAISS_BUCKET, QUERY_USAGE_TABLE_NAME, DYNAMODB_ENDPOINT

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fixed `test_first_query_allowed`: removed duplicate `dynamodb_table` fixture parameter (the test creates its own `mock_aws()` context; using both caused `ResourceInUseException` from nested contexts sharing moto state).
- QueryUsage DynamoDB table uses SK attribute `"date"` (not `"sk"`) — confirmed from CDK stack `infra/stacks/strengthwise_stack.py:47`.

### Completion Notes List

- Implemented full dual-source RAG pipeline: FAISS knowledge search + DynamoDB personal session retrieval + Claude claude-sonnet-4-5-20250514 generation.
- `backend/middleware/sanitize.py`: regex-based injection stripping + delimiter escaping + 2000-char truncation, called from router.
- `backend/models/query_models.py`: `QueryRequest`, `PersonalCitation`, `KnowledgeCitation`, `Citations`, `CoachingResponse` — all with `to_camel` alias_generator.
- `backend/services/rate_limit_service.py`: atomic DynamoDB `UpdateItem` with `ConditionalCheckFailedException` guard; SK is `"date"` per CDK schema; onboarding tier (7 days, limit=10) vs free tier (limit=3).
- `backend/services/rag_service.py`: module-level FAISS index load (S3 fallback for Lambda cold start), module-level `SentenceTransformer("all-MiniLM-L6-v2")`, full orchestration pipeline, JSON-structured Claude prompt with medical disclaimer, defensive JSON parse fallback.
- `backend/routers/query.py`: thin router — sanitize → rate limit check → RAG service → error handling; `queriesRemaining` injected from rate limit result.
- `backend/main.py`: registered `query_router`.
- Tests: 9 new tests added (6 sanitize + 3 rate limit + 5 query endpoint). All 36 tests pass (27 existing + 9 new), 5 skipped (FAISS index not built), zero regressions.

### File List

- `backend/middleware/sanitize.py` (NEW)
- `backend/models/query_models.py` (NEW)
- `backend/services/rate_limit_service.py` (NEW)
- `backend/services/rag_service.py` (NEW)
- `backend/routers/query.py` (NEW)
- `backend/main.py` (MODIFIED — added query_router import and registration)
- `backend/tests/test_sanitize.py` (NEW)
- `backend/tests/test_rate_limit.py` (NEW)
- `backend/tests/test_query.py` (NEW)

## Change Log

- 2026-04-26: Implemented Story 3.2 — Dual-Source RAG Pipeline. Created sanitize middleware, query Pydantic models, rate limit service (atomic DynamoDB), RAG service (FAISS + Claude), query router, and 9 new tests. All 36 tests pass.
