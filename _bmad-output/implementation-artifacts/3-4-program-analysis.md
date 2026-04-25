# Story 3.4: Program Analysis

Status: review

## Story

As an **athlete**,
I want to paste a training program and receive an evaluation against general principles and my personal training patterns,
so that I can assess program quality before committing to it.

## Acceptance Criteria

1. **Given** I am in the Chat interface **When** I paste a multi-line training program (up to 2000 characters) into the ChatInputBar **Then** the input expands to accommodate the text (max 200px height, already implemented in Story 3.3 textarea auto-expand) and I can submit it (FR12)

2. **Given** I submit a program for analysis via `POST /analyze` **When** the system processes it **Then** the response evaluates the program against general principles (amber/knowledge citations) and my personal training patterns (blue/personal citations), with specific recommendations and suggested modifications

3. **Given** the program analysis response **When** it renders in the chat **Then** it uses the same CitationBlock styling, FollowupChip pattern, and confidence framing as regular coaching queries — consistent UI across all query types

4. **Given** the program analysis request **When** processed by the backend **Then** it passes through the same input sanitization and rate limiting as `/query` (FR29, counts as one query against daily limit)

## Tasks / Subtasks

- [x] Task 1: Add `AnalyzeRequest` Pydantic model to `backend/models/query_models.py` (AC: #4)
  - [x] 1.1: Add to `query_models.py`:
    ```python
    class AnalyzeRequest(BaseModel):
        model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
        program: str = Field(..., max_length=2000)
    ```
  - [x] 1.2: Do NOT create a new file — add to the existing `query_models.py` alongside `QueryRequest`, `PersonalCitation`, etc.

- [x] Task 2: Add `analyze()` function to `backend/services/rag_service.py` (AC: #2)
  - [x] 2.1: Add `analyze(user_id: str, program_text: str) -> dict` — structurally mirrors `query()` but with a program-evaluation prompt
  - [x] 2.2: Reuse all private helpers: `_embed_query()`, `_search_knowledge()`, `_format_sessions()`, `_confidence_label()`, `_confidence_framing()`, `_call_gemini()`
  - [x] 2.3: Build a program-specific prompt — use `_build_analyze_prompt()` (new private function):
    ```python
    def _build_analyze_prompt(
        program_text: str,
        personal_context: str,
        session_count: int,
        knowledge_chunks: list[dict],
    ) -> str:
        knowledge_text = "\n".join(
            f"[{chunk.get('source', '')} — {chunk.get('principle', '')}]: {chunk.get('text', '')}"
            for chunk in knowledge_chunks
        )
        framing = _confidence_framing(session_count)
        return f"""You are StrengthWise, an AI strength coach. Evaluate the athlete's training program using general strength science principles and their personal training history.

    TRAINING PROGRAM TO EVALUATE:
    {program_text}

    ATHLETE'S PERSONAL TRAINING DATA ({session_count} sessions):
    {personal_context}

    STRENGTH SCIENCE KNOWLEDGE:
    {knowledge_text}

    {framing}

    Respond with a JSON object in this exact format:
    {{
      "response": "Your program evaluation here (2-4 paragraphs). Cover: alignment with principles, fit with athlete's current patterns, specific modifications suggested. Include: StrengthWise provides training insights, not medical advice.",
      "personal_citations": [
        {{"sessionDate": "YYYY-MM-DD", "exercise": "exercise name", "detail": "specific metric or observation"}}
      ],
      "knowledge_citations": [
        {{"source": "filename.md", "principle": "section header"}}
      ]
    }}

    Rules:
    - Evaluate program structure, volume, intensity, and exercise selection
    - Only cite sessions that relate to the exercises or patterns in the submitted program
    - Only cite knowledge chunks provided above
    - If data is insufficient, acknowledge it honestly; return empty citation arrays
    - Return ONLY the JSON object, no markdown code blocks"""
    ```
  - [x] 2.4: Implement `analyze()` with same error handling as `query()` — catch exceptions, raise `RuntimeError("AI_UNAVAILABLE")` on AI failure:
    ```python
    def analyze(user_id: str, program_text: str) -> dict:
        try:
            query_emb = _embed_query(program_text)
            knowledge_chunks = _search_knowledge(query_emb)
            sessions = session_service.get_sessions(user_id)
            personal_context, session_count = _format_sessions(sessions)
            prompt = _build_analyze_prompt(program_text, personal_context, session_count, knowledge_chunks)
            parsed = _call_gemini(prompt)
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                raise
            logger.error("Gemini API error in analyze: %s", exc)
            raise RuntimeError("AI_UNAVAILABLE") from exc

        personal_citations = [
            {"sessionDate": c.get("sessionDate", ""), "exercise": c.get("exercise", ""), "detail": c.get("detail", "")}
            for c in parsed.get("personal_citations", [])
        ]
        knowledge_citations = [
            {"source": c.get("source", ""), "principle": c.get("principle", "")}
            for c in parsed.get("knowledge_citations", [])
        ]

        return {
            "response": parsed.get("response", ""),
            "citations": {
                "personal": personal_citations,
                "knowledge": knowledge_citations,
            },
            "confidence": _confidence_label(session_count),
        }
    ```

- [x] Task 3: Create `backend/routers/analyze.py` (AC: #4)
  - [x] 3.1: Mirror the structure of `backend/routers/query.py` exactly — thin router, calls service, applies sanitization and rate limiting:
    ```python
    from fastapi import APIRouter, Depends, HTTPException

    import services.rag_service as rag_service
    import services.rate_limit_service as rate_limit_service
    from middleware.auth import CurrentUser, get_current_user
    from middleware.sanitize import sanitize_llm_input
    from models.query_models import AnalyzeRequest

    router = APIRouter(prefix="/analyze", tags=["analyze"])


    @router.post("", status_code=200)
    async def create_analysis(
        body: AnalyzeRequest,
        current_user: CurrentUser = Depends(get_current_user),
    ):
        sanitized = sanitize_llm_input(body.program)
        rate_result = rate_limit_service.check_and_increment(current_user)
        if not rate_result["allowed"]:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Daily query limit reached",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "detail": {"resetAt": rate_result["reset_at"], "limit": 3},
                },
            )
        try:
            result = rag_service.analyze(current_user, sanitized)
        except RuntimeError:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "I couldn't process that question right now. Please try again.",
                    "code": "AI_UNAVAILABLE",
                },
            )
        result["queriesRemaining"] = rate_result["queries_remaining"]
        result["tierLimit"] = rate_result["tier_limit"]
        return {"data": result}
    ```
  - [x] 3.2: `sanitize_llm_input` is called on `body.program` (the field name in `AnalyzeRequest`), not `body.query`

- [x] Task 4: Register the analyze router in `backend/main.py` (AC: #4)
  - [x] 4.1: Import `analyze_router` and include it:
    ```python
    from routers.analyze import router as analyze_router
    # ...
    app.include_router(analyze_router)
    ```
  - [x] 4.2: Add after the existing `app.include_router(query_router)` line

- [x] Task 5: Add `postAnalyze` to `frontend/src/api.js` (AC: #1, #2)
  - [x] 5.1: Add `postAnalyze(programText)` directly below `postQuery` — same raw fetch pattern (NOT `apiFetch`) for 429 handling:
    ```js
    export async function postAnalyze(programText) {
      const url = `${BASE_URL}/analyze`
      const token = await getToken()
      const headers = { 'Content-Type': 'application/json' }
      if (token) headers['Authorization'] = `Bearer ${token}`
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ program: programText }),
      })
      if (response.status === 429) {
        const body = await response.json()
        throw Object.assign(new Error('RATE_LIMIT_EXCEEDED'), { code: 'RATE_LIMIT_EXCEEDED', detail: body.detail })
      }
      if (!response.ok) throw new Error('AI_UNAVAILABLE')
      return response.json()
    }
    ```
  - [x] 5.2: The request body key is `program` (not `query`) — matches `AnalyzeRequest.program` in the backend Pydantic model
  - [x] 5.3: Do NOT modify `apiFetch`, `getExercises`, `createSession`, `getSessions`, `getSession`, or `postQuery`

- [x] Task 6: Add program analysis mode detection in `frontend/src/pages/Chat.jsx` (AC: #1, #2, #3)
  - [x] 6.1: Import `postAnalyze` at the top: `import { postQuery, postAnalyze, getSessions } from '../api'`
  - [x] 6.2: Program detection logic — detect multi-line input (contains `\n`) as program analysis:
    ```js
    const isProgram = inputText.includes('\n')
    ```
  - [x] 6.3: In the send query flow, route based on `isProgram`:
    ```js
    const result = isProgram
      ? await postAnalyze(inputText)
      : await postQuery(inputText)
    ```
  - [x] 6.4: The response JSON structure from `/analyze` is **identical** to `/query`: `{ data: { response, citations: { personal, knowledge }, confidence, queriesRemaining } }` — no changes needed to `ChatBubble`, `CitationBlock`, or `FollowupChip`
  - [x] 6.5: Add a subtle visual label on the user ChatBubble when `isProgram` is true to indicate it was a program analysis. Add a small `"Program"` badge or append `" [Program Analysis]"` to the message label. Do NOT modify `ChatBubble.jsx` structure — just pass a prop or handle inline in Chat.jsx.
    - **Simpler approach**: Prepend `"📋 "` to the user bubble text when isProgram — or just show "Program Analysis" as a secondary label below the user message. Keep it minimal.
    - **Actually**: Skip the visual badge — the response content will be self-explanatory. Do NOT add extra UI. AC #3 says "consistent UI across all query types."
  - [x] 6.6: Reset the textarea height after submit — call the existing height reset logic (already in 3.3):
    ```js
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    ```

- [x] Task 7: Write tests for `backend/tests/test_analyze.py` (AC: #4)
  - [x] 7.1: Create `backend/tests/test_analyze.py` — mirror `test_query.py` structure exactly:
    - `test_analyze_returns_200_with_citations` — mock `rag_service.analyze` and `rate_limit_service.check_and_increment`
    - `test_analyze_returns_429_when_rate_limited` — mock rate limit denial
    - `test_analyze_returns_500_on_ai_failure` — mock `RuntimeError`
    - `test_analyze_requires_auth` — no bypass
    - `test_sanitization_applied_to_program` — verify injection patterns stripped from program field
  - [x] 7.2: Use the same `_bypass_client`, `aws_credentials`, `_MOCK_RATE_ALLOWED`, `_MOCK_RATE_DENIED` patterns from `test_query.py`
  - [x] 7.3: POST body uses `{"program": "..."}` not `{"query": "..."}`
  - [x] 7.4: Mock `services.rag_service.analyze` (not `rag_service.query`) in the patches

- [x] Task 8: Verify no regressions
  - [x] 8.1: `GET /query` endpoint must be UNCHANGED — verify `test_query.py` still passes
  - [x] 8.2: `frontend/src/api.js` existing functions (`postQuery`, `getExercises`, `createSession`, `getSessions`, `getSession`) must be UNCHANGED
  - [x] 8.3: `ChatBubble.jsx`, `CitationBlock.jsx`, `FollowupChip.jsx`, `QueryCounter.jsx`, `StarterPromptCard.jsx` — ZERO changes
  - [x] 8.4: `npm run build` passes cleanly (90 modules, no errors)
  - [x] 8.5: Run `pytest backend/tests/` — all 5 new analyze tests pass; 4 pre-existing failures in test_query.py and test_rate_limit.py confirmed pre-existing (not introduced by this story)

## Dev Notes

### CRITICAL: AI Backend Uses Gemini, NOT Claude

Despite the architecture doc saying "Claude API", the actual implementation in `backend/services/rag_service.py` uses **Google Gemini** via `from google import genai`. The config shows `GEMINI_MODEL` env var. When adding `analyze()` to `rag_service.py`:

- Use `_call_gemini(prompt)` — the existing private function
- Do NOT import Anthropic SDK or add any Claude code
- Do NOT change `_call_gemini()` — reuse as-is

### What Already Exists (DO NOT RECREATE)

**Backend:**
- `backend/routers/query.py` — complete, DO NOT TOUCH
- `backend/services/rag_service.py` — extend with new `analyze()` and `_build_analyze_prompt()` functions only
- `backend/models/query_models.py` — extend with `AnalyzeRequest` only
- `backend/middleware/sanitize.py::sanitize_llm_input()` — reuse, DO NOT CHANGE
- `backend/services/rate_limit_service.py::check_and_increment()` — reuse, DO NOT CHANGE
- `backend/services/session_service.py::get_sessions()` — reuse in `analyze()`, DO NOT CHANGE

**Frontend:**
- `frontend/src/api.js::postQuery()` — DO NOT TOUCH, just add `postAnalyze()` below it
- `frontend/src/pages/Chat.jsx` — minimal surgical change: import `postAnalyze`, add `isProgram` detection, route conditionally
- ALL components (`ChatBubble`, `CitationBlock`, `FollowupChip`, `QueryCounter`, `StarterPromptCard`) — ZERO changes needed; response schema is identical

### Rate Limiting: analyze Counts Against Same Daily Limit

The `/analyze` endpoint uses the **same** `rate_limit_service.check_and_increment(current_user)` call. This means program analysis queries count against the same daily limit as regular chat queries. The response includes `queriesRemaining` and `tierLimit` just like `/query`.

### Request/Response Contract

**Request** `POST /analyze`:
```json
{ "program": "Day 1: Squat 5x5 @ 80%\nDay 2: Bench 4x6\nDay 3: Deadlift 3x3 @ 85%" }
```

**Response** (identical structure to `/query`):
```json
{
  "data": {
    "response": "Program evaluation text with medical disclaimer...",
    "citations": {
      "personal": [{ "sessionDate": "2026-04-15", "exercise": "Squat", "detail": "3x5 @ 100kg, RPE 8" }],
      "knowledge": [{ "source": "powerlifting.md", "principle": "Intensity Zones" }]
    },
    "confidence": "low",
    "queriesRemaining": 1,
    "tierLimit": 20
  }
}
```

Frontend accesses as: `data.data.response`, `data.data.citations.personal`, `data.data.queriesRemaining` — same as `postQuery`.

### Program Detection in Chat.jsx

The `isProgram` check uses newline detection:
```js
const isProgram = inputText.includes('\n')
```

This is simple and user-driven: if the user pasted multi-line text, it's a program. If they typed a single-line question, it's a query. No explicit UI toggle needed — the textarea already supports multi-line from Story 3.3.

The routing in the send handler changes only these two lines:
```js
// Before (Story 3.3):
const result = await postQuery(inputText)

// After (Story 3.4):
const isProgram = inputText.includes('\n')
const result = isProgram ? await postAnalyze(inputText) : await postQuery(inputText)
```

### File Locations

Files to CREATE:
```
backend/routers/analyze.py           ← NEW
backend/tests/test_analyze.py        ← NEW
```

Files to MODIFY (minimally):
```
backend/services/rag_service.py      ← ADD analyze() + _build_analyze_prompt() ONLY
backend/models/query_models.py       ← ADD AnalyzeRequest class ONLY
backend/main.py                      ← ADD 2 lines: import + app.include_router
frontend/src/api.js                  ← ADD postAnalyze() function ONLY
frontend/src/pages/Chat.jsx          ← ADD isProgram detection + conditional routing ONLY
```

Files NOT to touch:
```
backend/routers/query.py
backend/services/session_service.py
backend/services/rate_limit_service.py
backend/middleware/sanitize.py
backend/middleware/auth.py
frontend/src/components/ChatBubble.jsx
frontend/src/components/CitationBlock.jsx
frontend/src/components/FollowupChip.jsx
frontend/src/components/QueryCounter.jsx
frontend/src/components/StarterPromptCard.jsx
frontend/src/components/HeaderBar.jsx
frontend/src/components/TabBar.jsx
frontend/src/pages/Dashboard.jsx
frontend/src/pages/LogSession.jsx
frontend/src/pages/History.jsx
```

### Anti-Patterns to Avoid

- **DO NOT** duplicate `_call_gemini()` — it's already in `rag_service.py`, just call it from `analyze()`
- **DO NOT** duplicate `_embed_query()`, `_search_knowledge()`, `_format_sessions()`, `_confidence_label()`, `_confidence_framing()` — all private helpers are shared between `query()` and `analyze()`
- **DO NOT** create a new Pydantic model file — extend `query_models.py`
- **DO NOT** modify `ChatBubble.jsx` or any other component — the response schema is identical to `/query`
- **DO NOT** use `apiFetch` in `postAnalyze` — same reason as `postQuery`: 429 handling requires custom fetch with body parsing
- **DO NOT** add a separate "Analyze" button to the UI — the same ChatInputBar send button handles both modes via `isProgram` detection
- **DO NOT** add analyze logic to the existing `query()` function — keep them separate for prompt clarity

### Previous Story Intelligence (Story 3.3)

From Story 3.3 completion notes:
- `Chat.jsx` uses `-m-4` on root div to negate App.jsx `p-4` — do NOT change this layout trick
- Textarea auto-expand is already implemented in `Chat.jsx` via `handleInputChange` and `textareaRef` — works for pasted multi-line programs
- `postQuery` in api.js uses raw `fetch` (not `apiFetch`) for 429 body parsing — `postAnalyze` must follow the same pattern
- `getSessions()` uses `{ redirectOn401: false }` — do not change this
- All 10 Story 3.3 ACs are satisfied; `npm run build` passes at 90 modules

### References

- [Source: epics.md#Story 3.4] — All 4 acceptance criteria, FR12, FR29
- [Source: architecture.md#API Boundaries] — POST /analyze in analyze.py with rag_service + rate_limit_service
- [Source: architecture.md#Structure Patterns] — Routers are thin, business logic in services
- [Source: architecture.md#Enforcement Guidelines] — Use api.js wrapper, camelCase JSON, Pydantic models
- [Source: backend/routers/query.py] — Template for analyze.py router structure
- [Source: backend/services/rag_service.py] — All private helpers to reuse; _call_gemini() for LLM calls
- [Source: backend/models/query_models.py] — Add AnalyzeRequest alongside QueryRequest
- [Source: backend/tests/test_query.py] — Template for test_analyze.py test structure
- [Source: frontend/src/api.js] — postQuery pattern to replicate for postAnalyze
- [Source: implementation-artifacts/3-3-chat-interface-with-citation-display.md] — Chat.jsx structure and completion notes

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Added `AnalyzeRequest` Pydantic model to `query_models.py` — `program: str` field with max_length=2000, same camelCase alias config as `QueryRequest`
- Added `_build_analyze_prompt()` and `analyze()` to `rag_service.py` — reuses all 6 private helpers, no duplication; program-evaluation prompt distinct from coaching query prompt
- Created `backend/routers/analyze.py` — thin router mirroring `query.py` exactly; sanitization + rate limiting applied before service call
- Registered `analyze_router` in `main.py` after `query_router`
- Added `postAnalyze(programText)` to `api.js` — raw fetch pattern (not `apiFetch`), body key `program`, identical 429/error handling as `postQuery`
- Updated `Chat.jsx`: imported `postAnalyze`, added `isProgram = text.includes('\n')` detection, routes to `postAnalyze` or `postQuery` conditionally; response schema is identical so zero component changes needed
- Created `backend/tests/test_analyze.py` — 5 tests all passing; covers 200, 429, 500, auth, and sanitization
- Frontend build: 90 modules, no errors; no new modules since routing is within existing Chat.jsx
- Pre-existing test failures in `test_query.py` (2) and `test_rate_limit.py` (2) confirmed unrelated to this story — verified by running baseline before changes

### File List

Created:
- backend/routers/analyze.py
- backend/tests/test_analyze.py

Modified:
- backend/models/query_models.py
- backend/services/rag_service.py
- backend/main.py
- frontend/src/api.js
- frontend/src/pages/Chat.jsx

## Change Log

- 2026-04-26: Story 3.4 created — Program Analysis. Backend: new /analyze endpoint (analyze.py router + rag_service.analyze() function + AnalyzeRequest model). Frontend: postAnalyze() in api.js + isProgram detection in Chat.jsx. Identical response schema to /query — zero component changes needed.
