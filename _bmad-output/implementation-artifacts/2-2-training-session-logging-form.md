# Story 2.2: Training Session Logging Form

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **athlete**,
I want to log a training session with exercises, sets, reps, weight, RPE, and notes in under 30 seconds,
So that I can consistently capture my training data post-session without friction.

## Acceptance Criteria

1. **Given** I am on the logging form **When** I open it from the Log tab **Then** the date auto-fills to today, sport auto-selects from `localStorage.getItem('sw_last_sport')` (via `getSavedSport()` from SportSelector.jsx), and the form is ready for exercise entry (UX-DR13)

2. **Given** I have selected an exercise **When** it is added to the form **Then** an ExerciseBlock appears with the exercise name, a "Last: 4x3 @ 80kg" hint from my most recent session with that exercise, and set rows pre-filled with last session's weight/reps/RPE values (UX-DR6, UX-DR13)

3. **Given** I am entering set data **When** I interact with a SetEntryRow **Then** I see a 4-column grid (Set# | Weight | Reps | RPE) with monospace font, center-aligned numeric inputs, `inputmode="decimal"` for weight/RPE and `inputmode="numeric"` for reps (UX-DR5, UX-DR27)
   **And** Tab moves between fields left-to-right then down, Enter in the last field of a row adds a new set row

4. **Given** I have entered exercises and sets **When** I tap the "Save Session" button **Then** the session is saved via `POST /sessions`, I see an inline confirmation "Session saved. X sessions this month." in Green-500 text, and the form data is stored in DynamoDB Sessions table (userId PK, sk=`sessionDate#sessionId` SK)
   **And** the response completes in under 500ms (NFR1)

5. **Given** I have just saved a session **When** the confirmation appears **Then** I see a post-log nudge: "Ask me anything about your training" with a React Router `<Link>` to `/chat` (UX-DR17)

6. **Given** I am filling the form and submit with missing required fields **When** the validation error occurs **Then** inline error messages appear in Red-500 near the invalid fields without clearing any entered data (UX-DR19)

7. **Given** I want to add notes **When** I type in the notes textarea **Then** I can enter free-text up to 500 characters (NFR11), the textarea has `max-height: 120px` and scrolls if exceeded (FR4), and a character counter shows remaining chars

8. **Given** a typical 4-exercise session with 3-4 sets each **When** I use smart defaults and minimal edits **Then** the entire flow completes in under 30 seconds (NFR6) — sport and date are auto-filled, exercises pre-fill from last session

## Tasks / Subtasks

- [x] Task 1: Create Pydantic session models (AC: #4)
  - [x] 1.1: Create `backend/models/session_models.py`
  - [x] 1.2: `SetEntry` model: `set_number: int`, `weight: float | None = None`, `reps: int | None = None`, `rpe: float | None = None` — with `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)`
  - [x] 1.3: `ExerciseEntry` model: `exercise_id: str`, `exercise_name: str`, `sport_type: str`, `sets: list[SetEntry]` — same model_config
  - [x] 1.4: `SessionCreate` model: `session_date: str`, `sport: str`, `exercises: list[ExerciseEntry]` (min 1 item), `notes: str | None = Field(None, max_length=500)` — same model_config
  - [x] 1.5: `SessionResponse` model: `session_id: str`, `session_date: str`, `sport: str`, `exercises: list[ExerciseEntry]`, `notes: str | None = None`, `created_at: str` — same model_config
  - [x] 1.6: Use `from pydantic import BaseModel, ConfigDict, Field` and `from pydantic.alias_generators import to_camel` — same import pattern as `exercise_models.py`

- [x] Task 2: Create session service (AC: #4)
  - [x] 2.1: Create `backend/services/session_service.py`
  - [x] 2.2: `_get_table()` helper: creates `boto3.resource('dynamodb', region_name='us-east-1', endpoint_url=config.DYNAMODB_ENDPOINT if config.DYNAMODB_ENDPOINT else None).Table(config.SESSIONS_TABLE_NAME)` — called inside each function (not module-level) so moto can intercept in tests
  - [x] 2.3: `create_session(user_id: str, data: dict) -> dict`: generate `session_id = str(uuid.uuid4())`, `sk = f"{data['sessionDate']}#{session_id}"`, `created_at = datetime.utcnow().isoformat() + "Z"`, put_item to Sessions table, return the full item as a dict
  - [x] 2.4: `get_sessions(user_id: str) -> list[dict]`: query Sessions table with `KeyConditionExpression=Key('userId').eq(user_id)`, `ScanIndexForward=False` (newest first), return `response['Items']`
  - [x] 2.5: `get_session(user_id: str, session_id: str, session_date: str) -> dict | None`: get_item from Sessions table using PK=user_id and SK=`f"{session_date}#{session_id}"`, return Item or None
  - [x] 2.6: `get_month_count(user_id: str, year_month: str) -> int`: query with `KeyConditionExpression=Key('userId').eq(user_id) & Key('sk').begins_with(year_month)`, `Select='COUNT'`, return `response['Count']`
  - [x] 2.7: Import `import boto3`, `from boto3.dynamodb.conditions import Key`, `import uuid`, `from datetime import datetime`, `import config`

- [x] Task 3: Create sessions router (AC: #4)
  - [x] 3.1: Create `backend/routers/sessions.py`
  - [x] 3.2: `router = APIRouter(prefix="/sessions", tags=["sessions"])`
  - [x] 3.3: `POST /sessions` — accepts `SessionCreate` body, calls `session_service.create_session(user_id, session_data.model_dump(by_alias=True))`, calls `session_service.get_month_count(user_id, session_date[:7])`, returns **201** with `{"data": {"session": {...}, "monthCount": N}}`
  - [x] 3.4: `GET /sessions` — calls `session_service.get_sessions(user_id)`, returns 200 with `{"data": {"sessions": [...]}}`
  - [x] 3.5: `GET /sessions/{session_id}` — requires `session_date: str = Query(...)` query param, calls `session_service.get_session(user_id, session_id, session_date)`, returns 200 with `{"data": {"session": {...}}}` or 404 if None
  - [x] 3.6: All three endpoints: `Depends(get_current_user)` — auth required per NFR7
  - [x] 3.7: Router stays thin — no business logic beyond calling service and formatting response

- [x] Task 4: Register sessions router in main.py (AC: #4)
  - [x] 4.1: In `backend/main.py`, add `from routers.sessions import router as sessions_router`
  - [x] 4.2: Add `app.include_router(sessions_router)` — place after `app.include_router(exercises_router)`
  - [x] 4.3: Verify existing routes (`/health`, `/me`, `/exercises`) are unaffected

- [x] Task 5: Add moto dependency and write backend tests (AC: #4)
  - [ ] 5.1: Add `moto[dynamodb]` to `backend/requirements.txt` (needed for DynamoDB mocking in tests)
  - [ ] 5.2: Create `backend/tests/test_sessions.py`
  - [ ] 5.3: Add DynamoDB mock fixtures at top of test file:
    ```python
    import os
    import pytest
    import boto3
    from moto import mock_aws
    import config
    import middleware.auth as auth_module
    from fastapi.testclient import TestClient

    @pytest.fixture(autouse=True)
    def aws_credentials():
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

    @pytest.fixture
    def sessions_table():
        with mock_aws():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='Sessions',
                KeySchema=[
                    {'AttributeName': 'userId', 'KeyType': 'HASH'},
                    {'AttributeName': 'sk', 'KeyType': 'RANGE'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'sk', 'AttributeType': 'S'},
                ],
                BillingMode='PAY_PER_REQUEST',
            )
            yield table
    ```
  - [x] 5.4: Test `POST /sessions` with AUTH_BYPASS=true → 201, body has `data.session.sessionId`, `data.monthCount >= 1`
  - [x] 5.5: Test `GET /sessions` after creating 2 sessions → 200, body has `data.sessions` list length 2, ordered newest first
  - [x] 5.6: Test `POST /sessions` without auth (AUTH_BYPASS=false) → 401
  - [x] 5.7: Test `POST /sessions` with notes exceeding 500 chars → 422 (Pydantic validation)
  - [x] 5.8: Test `GET /sessions/{id}?session_date=...` → 200 with correct session
  - [x] 5.9: Use same `_bypass_client(monkeypatch)` helper pattern from `test_exercises.py`
  - [x] 5.10: All tests that call DynamoDB use `@mock_aws` decorator with `_make_sessions_table()` inside each test

- [x] Task 6: Create SetEntryRow component (AC: #3)
  - [x] 6.1: Create `frontend/src/components/SetEntryRow.jsx`
  - [x] 6.2: Props: `setNumber: number`, `weight: number|null`, `reps: number|null`, `rpe: number|null`, `onChange: ({weight, reps, rpe}) => void`, `onEnterLastField: () => void`
  - [x] 6.3: Render 4-column grid: `grid grid-cols-[40px_1fr_1fr_60px]` with `gap-1`
  - [x] 6.4: Col 1: set number label, `text-zinc-400 text-sm text-center self-center`
  - [x] 6.5: Cols 2-4: `<input>` elements with common focus/border classes
  - [x] 6.6: Weight input: `type="text"`, `inputMode="decimal"`, `placeholder="kg"`
  - [x] 6.7: Reps input: `type="text"`, `inputMode="numeric"`, `placeholder="reps"`
  - [x] 6.8: RPE input: `type="text"`, `inputMode="decimal"`, `placeholder="RPE"` — `onKeyDown`: if Enter key, call `onEnterLastField()`
  - [x] 6.9: Pre-filled values: controlled inputs. On change, parse float/int before calling `onChange`
  - [x] 6.10: Row height min 40px — `py-2` on inputs achieves this

- [x] Task 7: Create ExerciseBlock component (AC: #2, #3)
  - [x] 7.1: Create `frontend/src/components/ExerciseBlock.jsx`
  - [x] 7.2: Props: `exercise`, `initialSets`, `lastSessionHint`, `onChange`, `onRemove`
  - [x] 7.3: Internal state: `sets` array initialized from `initialSets` or default empty set
  - [x] 7.4: Header row: exercise name, remove button (`×`)
  - [x] 7.5: `lastSessionHint` shown below exercise name in `text-zinc-500 text-xs`
  - [x] 7.6: Column header row (Set | Weight | Reps | RPE)
  - [x] 7.7: Render `<SetEntryRow>` for each set; last row's Enter calls `addSet()`
  - [x] 7.8: `addSet()` copies last set's values for the new row
  - [x] 7.9: "＋ Add Set" button at bottom
  - [x] 7.10: On any set change, call `onChange(exerciseId, updatedSets)`
  - [x] 7.11: Container: `bg-zinc-800 rounded-lg p-3 mb-2`

- [x] Task 8: Implement LogSession.jsx page (AC: #1, #2, #4, #5, #6, #7, #8)
  - [x] 8.1: Replace stub in `frontend/src/pages/LogSession.jsx` with full implementation
  - [x] 8.2: All required state variables implemented
  - [x] 8.3: On mount: date=today, sport from getSavedSport(), getSessions() for history
  - [x] 8.4: exerciseHistory map built from sessions response
  - [x] 8.5: Date input with Zinc-800 styling
  - [x] 8.6: SportSelector with onChange clearing exerciseBlocks
  - [x] 8.7: ExercisePicker with selectedExerciseIds prop
  - [x] 8.8: handleAddExercise with history pre-fill and dedup
  - [x] 8.9: buildHint() function implemented
  - [x] 8.10: ExerciseBlock rendered per block with onChange/onRemove
  - [x] 8.11: Notes textarea with 500-char limit and counter
  - [x] 8.12: Save button with disabled/loading state
  - [x] 8.13: handleSave() with validation, createSession call, error handling
  - [x] 8.14: Session payload with exerciseId, exerciseName, sportType, filtered sets
  - [x] 8.15: Post-save confirmation with monthCount + chat nudge Link
  - [x] 8.16: All required imports present

- [x] Task 9: Add createSession and getSessions to api.js (AC: #4)
  - [x] 9.1: `createSession(sessionData)` added to `frontend/src/api.js`
  - [x] 9.2: `getSessions()` added to `frontend/src/api.js`
  - [x] 9.3: Both exported alongside `getExercises`

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow these exactly:**

- **DynamoDB Sessions table** is the only storage for sessions. PK=`userId` (String), SK=`sk` (String, value is `sessionDate#sessionId` e.g. `"2026-04-25#uuid4"`). Never use a different SK attribute name — architecture DynamoDB schema uses this compound SK for date-range queries.
- **Routers are thin.** `sessions.py` router: validate body via Pydantic, call service, return formatted response. Zero business logic in router.
- **camelCase JSON.** All request/response fields camelCase via `alias_generator=to_camel`. Python attribute `session_date` → JSON key `sessionDate`. `exercise_id` → `exerciseId`. Verify in tests.
- **Standard success response.** Wrap in `{"data": {...}}`. POST /sessions returns 201 with `{"data": {"session": {...}, "monthCount": N}}`. GET /sessions returns 200 with `{"data": {"sessions": [...]}}`.
- **Standard error response.** `{"error": "...", "code": "...", "detail": {...}}`. Use FastAPI's `HTTPException(status_code=..., detail={...})` pattern.
- **Auth on all endpoints.** All three session endpoints require `Depends(get_current_user)` — no unauthenticated access per NFR7.
- **POST /sessions returns 201.** Use `@router.post("", status_code=201)` — not 200.
- **`config.SESSIONS_TABLE_NAME`** is already defined in `backend/config.py` as `os.getenv("SESSIONS_TABLE_NAME", "Sessions")` — use this, not a hardcoded string.
- **`config.DYNAMODB_ENDPOINT`** is already defined in `backend/config.py` — pass as `endpoint_url` only if truthy (None for production, local DynamoDB URL for local dev).

### DynamoDB Item Schema

```
PK: userId         (String) — e.g. "test-user-001"
SK: sk             (String) — e.g. "2026-04-25#550e8400-e29b-41d4-a716-446655440000"
sessionId          (String) — uuid4, same as the uuid part of SK
sessionDate        (String) — ISO date "YYYY-MM-DD"
sport              (String) — "grip" | "armwrestling" | "powerlifting" | "general"
exercises          (List)   — list of exercise dicts (boto3 handles Python list natively)
notes              (String) — optional, omit key if None
createdAt          (String) — ISO 8601 UTC e.g. "2026-04-25T14:30:00Z"
```

DynamoDB item (Python dict for put_item with boto3.resource):
```python
item = {
    'userId': user_id,
    'sk': f"{session_date}#{session_id}",
    'sessionId': session_id,
    'sessionDate': session_date,
    'sport': data['sport'],
    'exercises': data['exercises'],  # boto3 serializes Python list/dict natively
    'createdAt': created_at,
}
if data.get('notes'):
    item['notes'] = data['notes']
table.put_item(Item=item)
```

### Backend Implementation Patterns

**session_service.py structure:**
```python
import uuid
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

import config


def _get_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.SESSIONS_TABLE_NAME)


def create_session(user_id: str, data: dict) -> dict:
    session_id = str(uuid.uuid4())
    session_date = data['sessionDate']
    sk = f"{session_date}#{session_id}"
    created_at = datetime.utcnow().isoformat() + 'Z'
    item = {
        'userId': user_id,
        'sk': sk,
        'sessionId': session_id,
        'sessionDate': session_date,
        'sport': data['sport'],
        'exercises': data['exercises'],
        'createdAt': created_at,
    }
    if data.get('notes'):
        item['notes'] = data['notes']
    _get_table().put_item(Item=item)
    return item


def get_sessions(user_id: str) -> list:
    response = _get_table().query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ScanIndexForward=False,  # newest first
    )
    return response['Items']


def get_session(user_id: str, session_id: str, session_date: str) -> dict | None:
    sk = f"{session_date}#{session_id}"
    response = _get_table().get_item(Key={'userId': user_id, 'sk': sk})
    return response.get('Item')


def get_month_count(user_id: str, year_month: str) -> int:
    response = _get_table().query(
        KeyConditionExpression=Key('userId').eq(user_id) & Key('sk').begins_with(year_month),
        Select='COUNT',
    )
    return response['Count']
```

**sessions.py router skeleton:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query

import services.session_service as session_service
from middleware.auth import CurrentUser, get_current_user
from models.session_models import SessionCreate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=201)
async def create_session(
    body: SessionCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    data = body.model_dump(by_alias=False)
    session = session_service.create_session(current_user, data)
    year_month = data['session_date'][:7]
    month_count = session_service.get_month_count(current_user, year_month)
    return {"data": {"session": session, "monthCount": month_count}}


@router.get("")
async def list_sessions(current_user: CurrentUser = Depends(get_current_user)):
    sessions = session_service.get_sessions(current_user)
    return {"data": {"sessions": sessions}}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session_date: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    session = session_service.get_session(current_user, session_id, session_date)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "Not found", "code": "NOT_FOUND"})
    return {"data": {"session": session}}
```

**Important:** `body.model_dump(by_alias=False)` returns Python snake_case keys (e.g. `session_date`, `exercise_id`). The DynamoDB item uses the snake_case form for internal storage but the service function accepts the dict. Be consistent — service uses snake_case internally, formats camelCase only in the API response layer.

Wait — actually to keep things simple and consistent with camelCase JSON storage in DynamoDB (since DynamoDB attributes are camelCase per architecture): call `body.model_dump(by_alias=True)` to get camelCase keys when storing to DynamoDB. Then the item stored has `exerciseId`, `exerciseName`, `sessionDate` as attribute values. This matches the DynamoDB naming convention (`camelCase` per architecture "Database Naming" section). Update task 3.3 accordingly: use `by_alias=True` when calling create_session.

**Correction on model_dump:** Use `body.model_dump(by_alias=True)` to produce camelCase dict for DynamoDB storage. This means `data['sessionDate']` not `data['session_date']`. Update `session_service.create_session` to use `data['sessionDate']`, `data['sport']`, `data['exercises']`, `data['notes']`.

### Testing Pattern for DynamoDB (Moto)

`moto` must be added to `backend/requirements.txt`. The `mock_aws` context manager patches boto3 globally — any boto3 call inside the context is intercepted.

**Critical:** `session_service._get_table()` creates a new boto3 resource each call (no module-level singleton). This is REQUIRED for moto to work — if boto3.resource() were called at import time, the mock would not be active yet.

Test pattern:
```python
def test_post_session_creates_item(monkeypatch, sessions_table):
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    
    with mock_aws():
        # Recreate table inside mock context (sessions_table fixture already does this)
        from main import app
        client = TestClient(app)
        
        payload = {
            "sessionDate": "2026-04-25",
            "sport": "grip",
            "exercises": [{
                "exerciseId": "grip-gripper-close",
                "exerciseName": "Gripper Close",
                "sportType": "grip",
                "sets": [{"setNumber": 1, "weight": 80.0, "reps": 3, "rpe": 9.0}]
            }],
            "notes": None
        }
        response = client.post("/sessions", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert "sessionId" in body["data"]["session"]
        assert body["data"]["monthCount"] == 1
```

**Note on moto fixture scope:** The `sessions_table` fixture uses `mock_aws()` as context manager. The TestClient must be created INSIDE the same `with mock_aws()` block — create the TestClient inside the test function, not in a shared fixture, when using moto. Alternatively, use `@mock_aws` decorator per test function.

### Frontend Implementation Patterns

**LogSession.jsx state and data flow:**
```
Mount → setDate(today), setSport(getSavedSport() || 'grip'), getSessions() → build exerciseHistory map
  ↓
User selects sport → SportSelector.onChange → setSport, saveSport, clear exerciseBlocks
  ↓
User picks exercise → ExercisePicker.onSelect → handleAddExercise:
  - look up exerciseHistory[exerciseId] for pre-fill sets + hint
  - push { exercise, sets: historySets || defaultSets, hint } to exerciseBlocks
  ↓
User edits sets → ExerciseBlock.onChange → update exerciseBlocks state
  ↓
User taps Save → handleSave:
  - validate ≥1 exercise with ≥1 set with reps
  - createSession(payload) → 201
  - setMazeResult({ monthCount }) → show confirmation + nudge
```

**exerciseHistory map building:**
```javascript
// sessions is response.data.sessions array (sorted newest first)
const map = {}
sessions.forEach(session => {
  (session.exercises || []).forEach(ex => {
    const id = ex.exerciseId
    if (!map[id]) {
      // First encounter = most recent session with this exercise
      map[id] = ex.sets || []
    }
  })
})
```

**Hint string builder:**
```javascript
function buildHint(sets) {
  if (!sets?.length) return null
  const { weight, reps } = sets[0]
  if (weight != null && reps != null) return `Last: ${sets.length}x${reps} @ ${weight}kg`
  if (reps != null) return `Last: ${sets.length}x${reps}`
  return null
}
```

**API call handling (try/catch pattern):**
```javascript
async function handleSave() {
  if (exerciseBlocks.length === 0) {
    setSaveError('Add at least one exercise before saving.')
    return
  }
  setSaving(true)
  setSaveError(null)
  try {
    const result = await createSession(payload)
    setSaveResult({ monthCount: result.data.monthCount })
    setExerciseBlocks([])
    setNotes('')
  } catch (err) {
    setSaveError('Failed to save session. Please try again.')
  } finally {
    setSaving(false)
  }
}
```

**Decimal handling in SetEntryRow:** Inputs are `type="text"` (not `type="number"`) to avoid mobile UX issues. Parse on change:
```javascript
const handleWeightChange = (e) => {
  const val = e.target.value
  onChange({ ...set, weight: val === '' ? null : parseFloat(val) })
}
```

### File Structure

Files this story creates or modifies:
```
backend/
├── models/
│   └── session_models.py         # NEW — SetEntry, ExerciseEntry, SessionCreate, SessionResponse
├── services/
│   └── session_service.py        # NEW — DynamoDB CRUD for sessions
├── routers/
│   └── sessions.py               # NEW — POST/GET /sessions, GET /sessions/{id}
├── tests/
│   └── test_sessions.py          # NEW — 5+ tests with moto DynamoDB mock
├── main.py                       # MODIFY — include sessions_router
└── requirements.txt              # MODIFY — add moto[dynamodb]

frontend/src/
├── components/
│   ├── SetEntryRow.jsx            # NEW — 4-col grid row (Set# | Weight | Reps | RPE)
│   └── ExerciseBlock.jsx          # NEW — exercise container with set rows + add-set button
└── pages/
    └── LogSession.jsx             # MODIFY (was stub) — full form implementation
frontend/src/api.js               # MODIFY — add createSession(), getSessions()
```

**NOT created in this story:**
- History.jsx implementation — deferred to Story 2.3
- Dashboard.jsx session cards — deferred to Story 2.3
- `GET /sessions` pagination — not needed for MVP (athletes have ≤500 sessions per architecture)
- Offline support / PWA — explicitly out of scope per UX spec

**Files from Story 2.1 used but NOT modified:**
- `frontend/src/components/SportSelector.jsx` — import `getSavedSport`, `saveSport` (named exports), and default `SportSelector`
- `frontend/src/components/ExercisePicker.jsx` — used as-is with `sportType`, `onSelect`, `selectedExerciseIds` props
- `frontend/src/api.js` — add to existing file (don't replace `getExercises`)

### Testing Requirements

**Backend (pytest with moto):**
- POST /sessions → 201, response has `data.session.sessionId`, `data.monthCount == 1`
- POST /sessions twice same month → second response has `monthCount == 2`
- GET /sessions → 200, `data.sessions` is list, sessions sorted newest first (check sk order)
- GET /sessions/{id}?session_date=... → 200 with correct session
- POST /sessions without auth (AUTH_BYPASS=false) → 401
- POST /sessions with notes > 500 chars → 422
- Assert camelCase: `body["data"]["session"]["sessionDate"]` not `session_date`
- Assert camelCase: `body["data"]["session"]["exercises"][0]["exerciseId"]` present

**Frontend (manual — no Vitest required for this story):**
- Open /log tab → date shows today, sport auto-selected from localStorage
- Select "Grip Sport" → ExercisePicker shows grip exercises
- Tap "Gripper Close" → ExerciseBlock appears with exercise name, set row pre-filled (or empty on first use)
- If previously logged Gripper Close → hint shows "Last: Nx3 @ 80kg"
- Fill weight/reps/RPE → Tab moves between fields, Enter in RPE adds new set row
- Add notes (optional)
- Tap Save → green button, loading state
- After save → "Session saved. X sessions this month." + chat nudge link visible
- Switch sport while exercises added → exercise blocks clear (no stale exercises from wrong sport)

### Previous Story Intelligence (Story 2.1)

**From Story 2.1 implementation — use these patterns exactly:**
- `Depends(get_current_user)` import: `from middleware.auth import CurrentUser, get_current_user`
- Router file location: `backend/routers/sessions.py` (same as `exercises.py`)
- `app.include_router()` in `backend/main.py` — follow exercises pattern
- Conftest TestClient: `TestClient(app)` from `main import app`
- Auth bypass: `monkeypatch.setattr(config, "AUTH_BYPASS", "true")` + `monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")`
- `api.js` uses `apiFetch()` wrapper — `createSession` and `getSessions` follow the same pattern as `getExercises`
- `SportSelector.jsx` exports `getSavedSport` and `saveSport` as named exports — import directly
- `ExercisePicker.jsx` accepts `sportType`, `onSelect`, `selectedExerciseIds` props — use these exact prop names
- Tailwind dark theme: Zinc-800 surfaces, Zinc-700 borders, Blue-500 active, Green-500 success, Red-500 error

**New patterns this story introduces:**
- DynamoDB CRUD via boto3.resource (first use of DynamoDB in project)
- moto mock_aws for DynamoDB testing
- POST endpoint returning 201
- React form with multiple dynamic children (exercise blocks)

### Anti-Patterns to Avoid

- **DO NOT** create the DynamoDB table in code — it's provisioned by CDK infra. In tests, moto creates it in-memory.
- **DO NOT** store exercises in a separate DynamoDB table — they live nested within the session item as a list.
- **DO NOT** use `boto3.client` — use `boto3.resource` for the high-level Table interface (simpler put_item/query API).
- **DO NOT** create the boto3 resource at module import level — create inside `_get_table()` so moto can intercept during tests.
- **DO NOT** use `type="number"` inputs for weight/reps/RPE — use `type="text"` with `inputMode` to avoid mobile browser issues (leading zeros, decimal formatting).
- **DO NOT** build LogSession as a single monolithic component — ExerciseBlock and SetEntryRow must be separate files per architecture component list.
- **DO NOT** add business logic to `sessions.py` router — thin router only: validate, call service, return.
- **DO NOT** use a Scan operation for DynamoDB — always Query with PK (`userId`) to stay O(user sessions) not O(table).
- **DO NOT** change App.jsx routing — `/log` route already points to LogSession. No routing changes needed.
- **DO NOT** modify SportSelector.jsx or ExercisePicker.jsx — use them as-is from Story 2.1.
- **DO NOT** call `getSessions()` inside `handleAddExercise` — load sessions once on mount only.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2] — Acceptance criteria, FR1-FR7, UX-DR5, UX-DR6, UX-DR13, UX-DR17, UX-DR19, UX-DR27, NFR1, NFR6, NFR11
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture] — Sessions table schema: PK=userId, SK=sessionDate#sessionId; access patterns; no scan
- [Source: _bmad-output/planning-artifacts/architecture.md#Service Boundaries] — session_service owns Sessions table reads/writes
- [Source: _bmad-output/planning-artifacts/architecture.md#Naming Patterns] — camelCase JSON/DynamoDB attributes, snake_case Python, PascalCase React
- [Source: _bmad-output/planning-artifacts/architecture.md#Format Patterns] — success `{"data":{}}`, error `{"error":"","code":"","detail":{}}`, POST returns 201
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Set Entry Row] — 4-col grid 40px|1fr|1fr|60px, row height 40px, monospace font
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Exercise Block] — Zinc-800, 8px radius, 10px padding, 8px margin-bottom, last-session hint
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Form Patterns] — Zinc-800 bg, Zinc-700 border, Blue-400 focus ring, Red-500 error, 16px font, 48px input height
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Touch Targets] — 44x44px minimum, 48px form inputs
- [Source: _bmad-output/implementation-artifacts/2-1-exercise-database-sport-selection.md#Dev Notes] — get_current_user pattern, conftest AUTH_BYPASS setup, apiFetch wrapper, getSavedSport/saveSport exports, ExercisePicker props
- [Source: backend/config.py] — SESSIONS_TABLE_NAME, DYNAMODB_ENDPOINT already defined; use these
- [Source: backend/tests/test_exercises.py] — _bypass_client helper pattern for auth bypass in tests

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Float→Decimal conversion: boto3.resource DynamoDB serializer rejects Python `float`; added `_to_decimal()` recursive helper in `session_service.py`
- Moto isolation in full suite: `test_config_from_env` calls `importlib.reload(config)` leaving `SESSIONS_TABLE_NAME="MySessions"` stale; fixed by calling `importlib.reload(config)` inside `_make_sessions_table()` to reset before each test
- moto approach: used `@mock_aws` decorator (not fixture-based `with mock_aws():`) since story notes recommend per-test decorator pattern; `_make_sessions_table()` called inside each decorated test

### Completion Notes List

- Backend: 4 new files, 2 modified — sessions router (POST/GET/GET-by-id), service (DynamoDB CRUD with Decimal handling), Pydantic models (camelCase via alias_generator), 7 tests all pass including auth guard, validation, camelCase assertion
- Frontend: 3 new files, 2 modified — SetEntryRow (4-col grid, type=text inputs), ExerciseBlock (set state management, add-set, hint display), LogSession (full form with history pre-fill, save+confirmation, chat nudge), api.js additions
- Key deviation from story template: used `@mock_aws` decorator per-test instead of `sessions_table` fixture (more reliable in full suite); used `by_alias=True` for DynamoDB camelCase storage per Dev Notes correction

### File List

- `backend/models/session_models.py` — NEW
- `backend/services/session_service.py` — NEW
- `backend/routers/sessions.py` — NEW
- `backend/tests/test_sessions.py` — NEW
- `backend/main.py` — MODIFIED (added sessions_router)
- `backend/requirements.txt` — MODIFIED (added moto[dynamodb])
- `frontend/src/components/SetEntryRow.jsx` — NEW
- `frontend/src/components/ExerciseBlock.jsx` — NEW
- `frontend/src/pages/LogSession.jsx` — MODIFIED (full implementation replacing stub)
- `frontend/src/api.js` — MODIFIED (added createSession, getSessions)

## Change Log

- 2026-04-25: Story 2.2 created — comprehensive story file with DynamoDB session CRUD, SetEntryRow/ExerciseBlock/LogSession frontend, moto testing pattern, pre-fill from history
- 2026-04-25: Story 2.2 implemented — backend (session models/service/router/tests), frontend (SetEntryRow, ExerciseBlock, LogSession, api.js); 22/22 backend tests passing
