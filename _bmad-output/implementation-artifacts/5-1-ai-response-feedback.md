# Story 5.1: AI Response Feedback

Status: review

## Story

As an **athlete**,
I want to give thumbs up or thumbs down on AI coaching responses,
So that the system can track response quality and improve over time.

## Acceptance Criteria

1. **Given** an AI coaching response is displayed in the Chat **When** I look below the response **Then** I see FeedbackButtons with thumbs up and thumbs down icons (UX-DR25)

2. **Given** I tap thumbs up or thumbs down **When** the feedback is submitted **Then** it is stored in the Feedback DynamoDB table (PK: queryId) with the rating and the button I tapped is visually highlighted as selected (FR28)

3. **Given** I have already provided feedback on a response **When** I view that response again **Then** my previous feedback selection is shown and no duplicate submission is possible

## Critical Context: What Already Exists — DO NOT RECREATE

**`config.py`** — `FEEDBACK_TABLE_NAME` ALREADY EXISTS:
```python
FEEDBACK_TABLE_NAME = os.getenv("FEEDBACK_TABLE_NAME", "Feedback")
```
Do NOT add this to config.py — it's already there.

**`frontend/src/components/FeedbackButtons.jsx`** — DOES NOT EXIST YET, must be created.

**`backend/routers/feedback.py`** — DOES NOT EXIST YET, listed in architecture's planned routers.

**`backend/services/feedback_service.py`** — DOES NOT EXIST YET, must be created.

**`backend/services/rag_service.py`** — EXISTS, needs ONE addition: generate and return `queryId` (uuid4).

**`backend/routers/query.py`** — EXISTS, thin router calling rag_service. Already passes `queriesRemaining` and `tierLimit` from rate_limit result. The `queryId` from rag_service flows through automatically (rag_service dict is spread into result).

**`frontend/src/pages/Chat.jsx`** — EXISTS. Messages stored as `{ role, content, citations, confidence }`. Must add `queryId` to AI message objects.

**`frontend/src/components/ChatBubble.jsx`** — EXISTS. Renders AI response + citations + followup chips. Must accept `queryId` prop and render `FeedbackButtons` below followup chips.

**`frontend/src/api.js`** — EXISTS. Uses `apiFetch(path, options)` pattern. Add `postFeedback()`.

**DynamoDB Feedback table schema** (from architecture):
- PK: `queryId` (S)
- No SK
- Additional attributes: `userId`, `rating` ("up" | "down"), `timestamp`

**`backend/tests/test_query.py`** — pattern reference:
```python
def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)
```

**`middleware/auth.py`** — EXISTS:
- `get_current_user` dependency — returns `str` (userId only). USE THIS for feedback router (simple auth, no tier detection needed).
- `get_user_context` — NOT needed here; feedback doesn't need tier or create date.

## Critical Design Decisions

### queryId Generation

Generate `queryId` as a UUID4 string inside `rag_service.query()` AND `rag_service.analyze()`. Include it in the returned dict so it flows through `query.py` and `analyze.py` routers to the frontend automatically.

```python
# In rag_service.query() and rag_service.analyze(), add to return dict:
import uuid
...
return {
    "queryId": str(uuid.uuid4()),
    "response": ...,
    "citations": ...,
    "confidence": ...,
}
```

The `query.py` router already spreads the rag_service result into the response:
```python
result = rag_service.query(user_context["user_id"], sanitized)
result["queriesRemaining"] = rate_result["queries_remaining"]
result["tierLimit"] = rate_result.get("tier_limit", 3)
return {"data": result}
```
So `queryId` will appear in `data.queryId` automatically — NO changes needed to `query.py` or `analyze.py` routers.

### "No Duplicate Submissions" Scope

Chat history lives in component state (cleared on page refresh — per architecture, this is MVP behavior). "No duplicate" means: within a single chat session, once feedback is submitted for a response, lock the buttons to show the selection. Backend idempotency is handled via DynamoDB `put_item` (last-write-wins on same `queryId`). Do NOT implement a GET /feedback endpoint or load historical feedback on mount — that's out of scope.

### FeedbackButtons UX

- Two icon buttons: 👍 (thumbs up) and 👎 (thumbs down)
- Default state: both Zinc-400, no fill
- After selection: selected button turns Blue-400 (thumbs up) or Amber-400 (thumbs down); buttons disabled; no spinner needed (fire-and-forget pattern)
- On API error: silently fail (log to console), keep selection shown locally — do NOT show error to user for feedback failure
- Size: small (16px icon, 28px touch target minimum)

### POST /feedback API Contract

```
POST /feedback
Authorization: Bearer <JWT>
Content-Type: application/json

Request body:
{
  "queryId": "uuid-string",
  "rating": "up" | "down"
}

Response 200:
{ "data": { "queryId": "uuid-string", "rating": "up" } }

Response 400: invalid rating value
Response 401: not authenticated
```

## Tasks / Subtasks

- [x] Task 1: Add `queryId` to `rag_service.py` responses
  - [x] 1.1: Add `import uuid` at the top of `backend/services/rag_service.py` (after existing imports)
  - [x] 1.2: In `rag_service.query()` return dict, add `"queryId": str(uuid.uuid4())` as the FIRST key:
    ```python
    return {
        "queryId": str(uuid.uuid4()),
        "response": parsed.get("response", ""),
        "citations": {"personal": personal_citations, "knowledge": knowledge_citations},
        "confidence": _confidence_label(session_count),
    }
    ```
  - [x] 1.3: In `rag_service.analyze()` return dict, add `"queryId": str(uuid.uuid4())` as the FIRST key (same pattern)
  - [x] 1.4: DO NOT change any other part of `rag_service.py` — query, analyze prompt building, Gemini call, session formatting all stay identical

- [x] Task 2: Create `backend/services/feedback_service.py` (NEW FILE)
  - [x] 2.1: Create the file following the EXACT `_get_table()` boto3 pattern from `profile_service.py`:
    ```python
    import boto3

    import config


    def _get_table():
        kwargs = {'region_name': 'us-east-1'}
        if config.DYNAMODB_ENDPOINT:
            kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
            kwargs['aws_access_key_id'] = 'fake'
            kwargs['aws_secret_access_key'] = 'fake'
        dynamodb = boto3.resource('dynamodb', **kwargs)
        return dynamodb.Table(config.FEEDBACK_TABLE_NAME)


    def submit_feedback(query_id: str, user_id: str, rating: str) -> None:
        from datetime import datetime, timezone
        _get_table().put_item(Item={
            'queryId': query_id,
            'userId': user_id,
            'rating': rating,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
    ```
  - [x] 2.2: `put_item` overwrites if same `queryId` already exists (DynamoDB last-write-wins) — no condition expression needed

- [x] Task 3: Create `backend/routers/feedback.py` (NEW FILE)
  - [x] 3.1: Create the router using `get_current_user` (not `get_user_context` — tier/date not needed):
    ```python
    from fastapi import APIRouter, Depends
    from pydantic import BaseModel, field_validator

    import services.feedback_service as feedback_service
    from middleware.auth import CurrentUser, get_current_user

    router = APIRouter(prefix="/feedback", tags=["feedback"])


    class FeedbackRequest(BaseModel):
        queryId: str
        rating: str

        @field_validator('rating')
        @classmethod
        def validate_rating(cls, v):
            if v not in ('up', 'down'):
                raise ValueError('rating must be "up" or "down"')
            return v


    @router.post("", status_code=200)
    async def submit_feedback(
        body: FeedbackRequest,
        user_id: CurrentUser = Depends(get_current_user),
    ):
        feedback_service.submit_feedback(body.queryId, user_id, body.rating)
        return {"data": {"queryId": body.queryId, "rating": body.rating}}
    ```

- [x] Task 4: Register feedback router in `backend/main.py`
  - [x] 4.1: Add import alongside existing router imports:
    ```python
    from routers.feedback import router as feedback_router
    ```
  - [x] 4.2: Add after `app.include_router(profile_router)`:
    ```python
    app.include_router(feedback_router)
    ```

- [x] Task 5: Add `postFeedback()` to `frontend/src/api.js`
  - [x] 5.1: Add after `getProfile()`:
    ```js
    export async function postFeedback(queryId, rating) {
      return apiFetch('/feedback', {
        method: 'POST',
        body: JSON.stringify({ queryId, rating }),
      })
    }
    ```

- [x] Task 6: Create `frontend/src/components/FeedbackButtons.jsx` (NEW FILE)
  - [x] 6.1: Create the component. It manages its own selected state; calls `postFeedback` on click; disables after selection:
    ```jsx
    import { useState } from 'react'
    import { postFeedback } from '../api'

    export default function FeedbackButtons({ queryId }) {
      const [selected, setSelected] = useState(null) // 'up' | 'down' | null

      async function handleFeedback(rating) {
        if (selected !== null || !queryId) return
        setSelected(rating)
        try {
          await postFeedback(queryId, rating)
        } catch {
          // silent fail — local selection already shown
        }
      }

      return (
        <div className="flex gap-2 mt-1" aria-label="Rate this response">
          <button
            onClick={() => handleFeedback('up')}
            disabled={selected !== null}
            aria-label="Thumbs up"
            aria-pressed={selected === 'up'}
            className={`text-base transition-colors disabled:cursor-default ${
              selected === 'up'
                ? 'text-blue-400'
                : selected !== null
                  ? 'text-zinc-600'
                  : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            👍
          </button>
          <button
            onClick={() => handleFeedback('down')}
            disabled={selected !== null}
            aria-label="Thumbs down"
            aria-pressed={selected === 'down'}
            className={`text-base transition-colors disabled:cursor-default ${
              selected === 'down'
                ? 'text-amber-400'
                : selected !== null
                  ? 'text-zinc-600'
                  : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            👎
          </button>
        </div>
      )
    }
    ```
  - [x] 6.2: `queryId` is required for API call. If undefined/null, button is still rendered but clicking is a no-op (the `if (!queryId)` guard handles this gracefully).

- [x] Task 7: Update `frontend/src/pages/Chat.jsx` to store `queryId` per AI message
  - [x] 7.1: Add `postFeedback` is NOT imported here — FeedbackButtons handles its own API call. No change needed to imports.
  - [x] 7.2: In `submitQuery()`, when setting the AI message, add `queryId` to the message object:
    ```js
    setMessages(prev => [
      ...prev,
      {
        role: 'ai',
        content: payload.response,
        citations: payload.citations,
        confidence: payload.confidence,
        queryId: payload.queryId ?? null,  // ADD THIS LINE
      },
    ])
    ```
  - [x] 7.3: Pass `queryId` from message to ChatBubble:
    ```jsx
    {messages.map((msg, i) => (
      <ChatBubble
        key={i}
        role={msg.role}
        message={msg.content}
        citations={msg.citations}
        followups={msg.role === 'ai' ? getFollowups(msg.confidence) : undefined}
        onFollowupSelect={handleFollowupSelect}
        queryId={msg.queryId}    // ADD THIS PROP
      />
    ))}
    ```
  - [x] 7.4: DO NOT change `submitQuery`, error handling, `queriesRemaining`, `tierLimit`, `resetAt`, the getSessions useEffect, the getProfile useEffect, or the textarea/button render logic.

- [x] Task 8: Update `frontend/src/components/ChatBubble.jsx` to render FeedbackButtons
  - [x] 8.1: Add FeedbackButtons import at the top:
    ```jsx
    import FeedbackButtons from './FeedbackButtons'
    ```
  - [x] 8.2: Accept `queryId` in the component signature:
    ```jsx
    export default function ChatBubble({ role, message, citations, followups, onFollowupSelect, queryId }) {
    ```
  - [x] 8.3: For AI bubbles, add `FeedbackButtons` AFTER the followup chips block:
    ```jsx
    {followups && followups.length > 0 && (
      <div className="flex flex-wrap gap-2 px-1">
        {followups.map((q, i) => (
          <FollowupChip key={i} question={q} onSelect={onFollowupSelect} />
        ))}
      </div>
    )}
    <FeedbackButtons queryId={queryId} />
    ```
  - [x] 8.4: DO NOT change the user bubble branch, citation rendering, the disclaimer text, or any other logic.

- [x] Task 9: Write backend tests
  - [x] 9.1: Create `backend/tests/test_feedback.py` (NEW FILE):
    - `test_feedback_thumbs_up_returns_200` — mock `feedback_service.submit_feedback`; POST `{"queryId": "test-query-id", "rating": "up"}`; assert 200 and `data.rating == "up"`
    - `test_feedback_thumbs_down_returns_200` — same but `"rating": "down"`
    - `test_feedback_invalid_rating_returns_422` — POST `{"queryId": "test-query-id", "rating": "neutral"}`; assert 422 (Pydantic validation)
    - `test_feedback_requires_auth` — no bypass; POST with no auth header; assert 401
    - `test_feedback_missing_query_id_returns_422` — POST `{"rating": "up"}` with no queryId; assert 422
  - [x] 9.2: Use `_bypass_client(monkeypatch)` pattern from `test_query.py`
  - [x] 9.3: Use `unittest.mock.patch("services.feedback_service.submit_feedback")` — do NOT set up real DynamoDB
  - [x] 9.4: `submit_feedback` returns `None` — mock with `return_value=None`

- [x] Task 10: Verify zero regressions
  - [x] 10.1: `pytest backend/tests/test_query.py` — must still pass (rag_service now returns queryId, mock in test_query.py returns `_MOCK_RAG_RESULT` which doesn't have queryId — this is fine, the router just omits it from response)
  - [x] 10.2: `pytest backend/tests/test_analyze.py` — must still pass (same reason)
  - [x] 10.3: `pytest backend/tests/test_profile.py` — must still pass
  - [x] 10.4: `pytest backend/tests/test_sessions.py` — must still pass
  - [x] 10.5: `pytest backend/tests/test_rate_limit.py` — must still pass
  - [x] 10.6: `pytest backend/tests/test_feedback.py` — all new tests pass

## Dev Notes

### CRITICAL: `queryId` in test_query.py Mock

`test_query.py` uses `_MOCK_RAG_RESULT` which does NOT include `queryId`. After Task 1, the real `rag_service.query()` will return `queryId`, but the mock does not. This is fine — `test_query.py` mocks `rag_service.query` entirely, so the UUID generation code is never reached. The response in test_query.py will simply not include `queryId` in `data`, which is acceptable (tests only assert on `response`, `citations`, `confidence`, `queriesRemaining` — they do not assert `queryId` is absent). Do NOT modify `test_query.py` or `_MOCK_RAG_RESULT`.

### CRITICAL: Use `get_current_user`, NOT `get_user_context` in feedback router

Feedback submission only needs `userId` to store who submitted it. `get_current_user` returns a `str` (userId) directly. Using `get_user_context` would add unnecessary overhead (Cognito attribute lookups). See `middleware/auth.py` — the `CurrentUser` type alias is `str`.

### CRITICAL: DynamoDB Table Name from config

ALWAYS use `config.FEEDBACK_TABLE_NAME` — NEVER hardcode `"Feedback"`. The config already defines this. The `_get_table()` pattern in `feedback_service.py` follows the identical pattern used in `profile_service.py` and `rate_limit_service.py`.

### FeedbackButtons: Fire-and-Forget Pattern

The feedback submission is non-critical. The pattern is:
1. User clicks → `setSelected(rating)` immediately (optimistic UI)
2. `await postFeedback(queryId, rating)` in background
3. On error: catch silently, do NOT revert `selected` state, do NOT show error

This matches the non-critical profile call pattern in `Chat.jsx` (catch block is intentional).

### FeedbackButtons: Renders on Every AI Message

`FeedbackButtons` is rendered for every AI bubble (both from `postQuery` and `postAnalyze`). Each instance has its own isolated `useState`, so selections are independent per message. The `queryId` prop uniquely identifies which response is being rated.

### API Response: queryId Now Appears in /query and /analyze

After Task 1, the responses from `POST /query` and `POST /analyze` will include `queryId` in `data`. This is a backwards-compatible additive change — existing frontend code ignoring `queryId` is unaffected.

### DynamoDB Feedback Table: Idempotent Writes

`put_item` on DynamoDB overwrites the existing item if `queryId` already exists. This means if a user somehow submits feedback twice (e.g., race condition), the last write wins. This is acceptable behavior — the UI already prevents this by disabling buttons after first click.

### File Structure

Files to CREATE:
```
backend/services/feedback_service.py
backend/routers/feedback.py
backend/tests/test_feedback.py
frontend/src/components/FeedbackButtons.jsx
```

Files to MODIFY:
```
backend/services/rag_service.py    ← ADD import uuid + queryId to return dicts (both query and analyze)
backend/main.py                    ← REGISTER feedback router
frontend/src/api.js                ← ADD postFeedback()
frontend/src/pages/Chat.jsx        ← ADD queryId to AI message state + prop to ChatBubble
frontend/src/components/ChatBubble.jsx  ← ADD FeedbackButtons import + render below followup chips
```

Files NOT to touch:
```
backend/routers/query.py           ← queryId flows through automatically from rag_service
backend/routers/analyze.py         ← queryId flows through automatically from rag_service
backend/config.py                  ← FEEDBACK_TABLE_NAME already exists
backend/middleware/auth.py         ← get_current_user already exists
backend/tests/test_query.py        ← mock doesn't return queryId, that's fine
backend/tests/test_analyze.py      ← same reason
frontend/src/components/QueryCounter.jsx
frontend/src/components/CitationBlock.jsx
frontend/src/components/FollowupChip.jsx
frontend/src/components/TabBar.jsx
```

### Patterns from Previous Stories

- boto3 `_get_table()` helper: ALWAYS use `config.DYNAMODB_ENDPOINT` for local/prod parity; copy exactly from `profile_service.py`
- Pydantic `field_validator` for request validation (see `query_models.py` for reference)
- Test auth bypass: `monkeypatch.setattr(config, "AUTH_BYPASS", "true")` + `monkeypatch.setattr(auth_module, "_jwks_cache", None)`
- `from main import app` AFTER monkeypatching config
- API response wrapper: always `{ "data": { ... } }`
- camelCase JSON keys: `queryId` (not `query_id`), `rating`

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-6

### Completion Notes List
- Added `import uuid` and `"queryId": str(uuid.uuid4())` to both `rag_service.query()` and `rag_service.analyze()` return dicts — queryId now flows automatically through query.py and analyze.py routers to the frontend.
- Created `feedback_service.py` using the identical `_get_table()` boto3 pattern from `profile_service.py`; DynamoDB put_item is idempotent (last-write-wins on same queryId).
- Created `feedback.py` router with Pydantic `field_validator` constraining rating to "up"/"down"; uses `get_current_user` (not `get_user_context`) since tier/date not needed.
- Registered `feedback_router` in `main.py` after existing routers.
- Added `postFeedback()` to `api.js` using the standard `apiFetch` wrapper.
- Created `FeedbackButtons.jsx` with optimistic UI (setSelected before await), fire-and-forget pattern, and silent error catch. Buttons disabled after first selection; unselected button dims to zinc-600.
- Updated `Chat.jsx` to store `queryId: payload.queryId ?? null` on AI message objects and pass `queryId={msg.queryId}` to ChatBubble.
- Updated `ChatBubble.jsx` to import FeedbackButtons and render `<FeedbackButtons queryId={queryId} />` after the followup chips block (AI bubble only).
- All 5 new backend tests pass; all 29 existing regression tests pass with zero failures.

### File List
- backend/services/rag_service.py (modified)
- backend/services/feedback_service.py (created)
- backend/routers/feedback.py (created)
- backend/main.py (modified)
- backend/tests/test_feedback.py (created)
- frontend/src/api.js (modified)
- frontend/src/components/FeedbackButtons.jsx (created)
- frontend/src/pages/Chat.jsx (modified)
- frontend/src/components/ChatBubble.jsx (modified)
- _bmad-output/implementation-artifacts/sprint-status.yaml (modified)

## Change Log

- 2026-04-26: Story 5.1 created — AI Response Feedback. Adds POST /feedback endpoint, FeedbackButtons component, queryId in query/analyze responses, and feedback submission from Chat UI.
- 2026-04-26: Implementation complete. All 10 tasks checked. 5 new backend tests pass; 29 existing tests pass (zero regressions). Story status → review.
