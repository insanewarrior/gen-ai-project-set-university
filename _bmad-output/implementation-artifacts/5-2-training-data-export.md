# Story 5.2: Training Data Export

Status: review

## Story

As an **athlete**,
I want to export all my training data as a CSV file,
So that I own my data and can use it outside StrengthWise.

## Acceptance Criteria

1. **Given** I trigger a data export via `POST /export` **When** the export completes **Then** I receive a CSV file containing all my training sessions with date, sport, exercise, set number, weight, reps, RPE, and notes (FR21)

2. **Given** the exported CSV file **When** I open it in Excel, Google Sheets, or another spreadsheet tool **Then** it opens correctly with proper column headers and data formatting — standards-compliant CSV (NFR24)

3. **Given** I trigger export in the frontend **When** the request is processing **Then** I see "Preparing your export..." inline, then a download link appears when ready (UX-DR26)

---

## Critical Context: What Already Exists — DO NOT RECREATE

**`session_service.get_sessions(user_id)`** — ALREADY EXISTS in `backend/services/session_service.py`:
```python
def get_sessions(user_id: str) -> list:
    response = _get_table().query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ScanIndexForward=False,
    )
    return response['Items']
```
Call this directly from `export_service`. Do NOT write a new DynamoDB query.

**`config.SESSIONS_TABLE_NAME`** — ALREADY EXISTS in `backend/config.py`. Use it if you need `_get_table()` (but prefer calling `session_service.get_sessions()` directly).

**`get_current_user`** — ALREADY EXISTS in `middleware/auth.py`. Returns `CurrentUser = str` (userId). Use this for the export router (no tier/date needed — same as feedback router).

**`backend/routers/export.py`** — DOES NOT EXIST yet, must be created.

**`backend/services/export_service.py`** — DOES NOT EXIST yet, must be created.

**`frontend/src/pages/Profile.jsx`** — EXISTS. This is where the export button belongs. Add the export UI here (export button + inline status).

**`frontend/src/api.js`** — EXISTS. Add `exportTrainingData()`. NOTE: This function CANNOT use `apiFetch()` (which parses JSON). It must use raw `fetch` returning a Blob for browser download. See exact pattern below.

**`backend/main.py`** — EXISTS. Register `export_router` after `feedback_router`.

---

## Critical Design Decisions

### DynamoDB Decimal Handling — CRITICAL

`session_service.get_sessions()` returns DynamoDB items. boto3's DynamoDB resource returns `Decimal` objects for all numeric fields (weight, rpe, setNumber, reps). The CSV writer cannot serialize `Decimal` directly.

**In `export_service.py`, convert before writing to CSV:**
```python
from decimal import Decimal

def _to_num(val):
    if val is None:
        return ''
    if isinstance(val, Decimal):
        f = float(val)
        return int(f) if f == int(f) else f
    return val
```
Apply `_to_num()` to every numeric field: `setNumber`, `weight`, `reps`, `rpe`.

### CSV Structure — One Row Per Set (Denormalized)

The DynamoDB session item structure (from `session_models.py`):
```
Session:
  sessionDate: str (e.g., "2026-04-15")
  sport: str
  notes: str | None
  exercises: list of:
    exerciseName: str
    sets: list of:
      setNumber: int
      weight: float | None
      reps: int | None
      rpe: float | None
```

**CSV output — one row per set:**
```
date,sport,exercise,set,weight,reps,rpe,notes
2026-04-15,grip,Gripper Close,1,80.0,3,9.0,felt strong
2026-04-15,grip,Gripper Close,2,80.0,3,8.5,felt strong
2026-04-15,grip,Hub Lift,1,25.0,5,,
```
- `notes` appears ONLY on the first set row of a session (all other set rows for that session leave notes empty)
- Empty fields: output `''` (nothing, not "None" or "null")
- DynamoDB field names use camelCase: `exerciseName`, `setNumber`, `weight`, `reps`, `rpe`

### FastAPI Response for CSV

Use `fastapi.Response` with `media_type="text/csv"`:
```python
from fastapi import Response
import csv, io

def generate_csv(sessions: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['date', 'sport', 'exercise', 'set', 'weight', 'reps', 'rpe', 'notes'])
    for session in sessions:
        session_date = session.get('sessionDate', '')
        sport = session.get('sport', '')
        notes = session.get('notes', '')
        first_set_of_session = True
        for exercise in session.get('exercises', []):
            exercise_name = exercise.get('exerciseName', '')
            for s in exercise.get('sets', []):
                row_notes = notes if first_set_of_session else ''
                first_set_of_session = False
                writer.writerow([
                    session_date,
                    sport,
                    exercise_name,
                    _to_num(s.get('setNumber', '')),
                    _to_num(s.get('weight')),
                    _to_num(s.get('reps')),
                    _to_num(s.get('rpe')),
                    row_notes,
                ])
    return output.getvalue()
```

**Router returns:**
```python
from fastapi import APIRouter, Depends, Response
from middleware.auth import CurrentUser, get_current_user
import services.session_service as session_service
import services.export_service as export_service

router = APIRouter(prefix="/export", tags=["export"])

@router.post("")
async def export_training_data(
    current_user: CurrentUser = Depends(get_current_user),
):
    sessions = session_service.get_sessions(current_user)
    csv_content = export_service.generate_csv(sessions)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=training-data.csv"},
    )
```

### Frontend Download Pattern — NOT apiFetch

`apiFetch()` calls `response.json()` — that breaks for CSV. Export needs raw `fetch` returning a Blob.

**Add to `frontend/src/api.js`:**
```js
export async function exportTrainingData() {
  const token = await getToken()
  const headers = { ...devHeaders() }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const response = await fetch(`${BASE_URL}/export`, { method: 'POST', headers })
  if (!response.ok) throw new Error(`API error: ${response.status}`)
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'training-data.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
```
Import `getToken` and `devHeaders` are already available in `api.js` — no new imports needed.

### Frontend UX — Profile.jsx

Export button goes in `Profile.jsx` (the profile page). Add below the query budget section:

```jsx
import { useState } from 'react'
import { exportTrainingData } from '../api'

// Inside Profile component:
const [exporting, setExporting] = useState(false)
const [exportError, setExportError] = useState(null)

async function handleExport() {
  setExporting(true)
  setExportError(null)
  try {
    await exportTrainingData()
  } catch {
    setExportError('Export failed. Please try again.')
  } finally {
    setExporting(false)
  }
}
```

```jsx
{/* Add after query budget section */}
<div className="bg-zinc-800 rounded-lg px-4 py-3 mt-4">
  <p className="text-zinc-400 text-xs mb-2">Your data</p>
  <button
    onClick={handleExport}
    disabled={exporting}
    className="w-full py-2 px-4 border border-blue-500 text-blue-400 rounded-lg text-sm hover:bg-blue-500/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
  >
    {exporting ? 'Preparing your export...' : 'Export Training Data (CSV)'}
  </button>
  {exportError && <p className="text-red-400 text-xs mt-2">{exportError}</p>}
</div>
```

Button style: Secondary tier (Blue-500 border, UX-DR18). State changes to "Preparing your export..." during request (UX-DR26). Error shown inline (UX-DR19).

---

## Tasks / Subtasks

- [x] Task 1: Create `backend/services/export_service.py` (NEW FILE)
  - [x] 1.1: Implement `_to_num(val)` helper to convert Decimal → float/int (empty string for None)
  - [x] 1.2: Implement `generate_csv(sessions: list) -> str` using `csv.writer` + `io.StringIO`
  - [x] 1.3: CSV headers: `['date', 'sport', 'exercise', 'set', 'weight', 'reps', 'rpe', 'notes']`
  - [x] 1.4: One row per set, notes only on first set row of each session
  - [x] 1.5: DO NOT call DynamoDB — accept sessions list as parameter (session_service fetches the data)

- [x] Task 2: Create `backend/routers/export.py` (NEW FILE)
  - [x] 2.1: `POST /export` with `get_current_user` dependency (not `get_user_context`)
  - [x] 2.2: Call `session_service.get_sessions(current_user)` → pass result to `export_service.generate_csv()`
  - [x] 2.3: Return `fastapi.Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=training-data.csv"})`
  - [x] 2.4: No Pydantic request model needed (POST with no body)

- [x] Task 3: Register export router in `backend/main.py`
  - [x] 3.1: Add `from routers.export import router as export_router`
  - [x] 3.2: Add `app.include_router(export_router)` after `app.include_router(feedback_router)`

- [x] Task 4: Add `exportTrainingData()` to `frontend/src/api.js`
  - [x] 4.1: Add `exportTrainingData()` function using raw `fetch` (NOT `apiFetch`) — see exact implementation above
  - [x] 4.2: Function must: call `getToken()`, attach auth header, POST to `/export`, get Blob, trigger browser download via `URL.createObjectURL`
  - [x] 4.3: Do NOT parse response as JSON

- [x] Task 5: Update `frontend/src/pages/Profile.jsx`
  - [x] 5.1: Add `useState` for `exporting` and `exportError` state variables
  - [x] 5.2: Import `exportTrainingData` from `'../api'`
  - [x] 5.3: Add `handleExport` async function (see pattern above)
  - [x] 5.4: Render export button section below the query budget `div`, using Secondary button style (Blue-500 border)
  - [x] 5.5: Button label: `exporting ? 'Preparing your export...' : 'Export Training Data (CSV)'`
  - [x] 5.6: Show inline error in Red-400 text if `exportError` is set
  - [x] 5.7: DO NOT change `getProfile()` call, stat rows, QueryCounter, or any existing logic

- [x] Task 6: Write backend tests
  - [x] 6.1: Create `backend/tests/test_export.py` (NEW FILE)
    - `test_export_returns_csv_content_type` — bypass auth; mock `session_service.get_sessions` with empty list; POST `/export`; assert 200, `response.headers["content-type"]` starts with `"text/csv"`
    - `test_export_empty_sessions_returns_headers_only` — mock `get_sessions` returning `[]`; assert CSV content equals `"date,sport,exercise,set,weight,reps,rpe,notes\r\n"`
    - `test_export_with_sessions_returns_set_rows` — mock `get_sessions` with one session containing one exercise with two sets; assert CSV has 2 data rows (plus header); assert correct values in first row
    - `test_export_requires_auth` — no bypass; POST `/export` without auth header; assert 401
    - `test_export_content_disposition` — bypass auth; mock `get_sessions` with `[]`; assert `Content-Disposition` header contains `"training-data.csv"`
  - [x] 6.2: Use `_bypass_client(monkeypatch)` pattern from `test_feedback.py`
  - [x] 6.3: Mock with `unittest.mock.patch("services.session_service.get_sessions", return_value=[...])`
  - [x] 6.4: Parse CSV from `response.text` using `csv.reader(io.StringIO(response.text))`

- [x] Task 7: Verify zero regressions
  - [x] 7.1: `pytest backend/tests/test_sessions.py` — must still pass
  - [x] 7.2: `pytest backend/tests/test_feedback.py` — must still pass
  - [x] 7.3: `pytest backend/tests/test_profile.py` — must still pass
  - [x] 7.4: `pytest backend/tests/test_export.py` — all new tests pass

---

## File Structure

Files to CREATE:
```
backend/services/export_service.py
backend/routers/export.py
backend/tests/test_export.py
```

Files to MODIFY:
```
backend/main.py                    ← REGISTER export_router
frontend/src/api.js                ← ADD exportTrainingData() (raw fetch, not apiFetch)
frontend/src/pages/Profile.jsx     ← ADD export button + inline status
```

Files NOT to touch:
```
backend/services/session_service.py   ← get_sessions() already works perfectly
backend/config.py                      ← SESSIONS_TABLE_NAME already exists
backend/middleware/auth.py             ← get_current_user already exists
backend/models/session_models.py       ← no changes needed
frontend/src/api.js (other functions)  ← do not change apiFetch or existing functions
```

---

## Patterns from Previous Stories

- **`_bypass_client(monkeypatch)` test pattern** — identical to `test_feedback.py`:
  ```python
  def _bypass_client(monkeypatch) -> TestClient:
      monkeypatch.setattr(config, "AUTH_BYPASS", "true")
      monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
      monkeypatch.setattr(auth_module, "_jwks_cache", None)
      from main import app
      return TestClient(app)
  ```

- **Router structure** — thin router calling service (same as `feedback.py`, `sessions.py`):
  ```python
  router = APIRouter(prefix="/export", tags=["export"])
  @router.post("") ...
  ```

- **`get_current_user`** — for endpoints needing only userId (not tier/date). Returns `str`. See `feedback.py` for reference.

- **AWS credentials in tests** — `autouse` fixture (already in `conftest.py` or add to test file):
  ```python
  @pytest.fixture(autouse=True)
  def aws_credentials():
      os.environ["AWS_ACCESS_KEY_ID"] = "testing"
      ...
  ```

---

## Dev Notes

### CRITICAL: `apiFetch` vs Raw Fetch for Export

`apiFetch()` in `api.js` calls `response.json()` at the end — this throws if the response is CSV. The export function MUST use raw `fetch`, get the `blob()`, and trigger a browser download. DO NOT refactor `apiFetch` to handle both cases.

### CRITICAL: Decimal Conversion

boto3 DynamoDB resource serializes all numbers as `Decimal`. When building CSV rows from session items:
- `s.get('setNumber')` → Decimal — call `_to_num()`
- `s.get('weight')` → Decimal or None — call `_to_num()`  
- `s.get('reps')` → Decimal or None — call `_to_num()`
- `s.get('rpe')` → Decimal or None — call `_to_num()`

The `_to_num()` helper returns `''` for None, and converts Decimal to int (if whole number) or float.

### CRITICAL: Notes Only on First Set Row

To avoid repeating notes on every set row, track a boolean `first_set_of_session = True`, reset it per session. Output notes on the first set row of the session only (then set flag to False). This makes the CSV readable in spreadsheets without cluttering every row.

### No Pydantic Request Model for Export

`POST /export` takes no request body — authentication is via JWT header only. No `BaseModel` needed. The endpoint simply calls `session_service.get_sessions()` for the authenticated user and returns CSV.

### Session Data Field Names in DynamoDB

DynamoDB items stored by `session_service.create_session()` use camelCase field names:
- `session.get('sessionDate')` — string, e.g., `"2026-04-15"`
- `session.get('sport')` — string
- `session.get('notes')` — optional string
- `session.get('exercises')` — list of exercise dicts:
  - `exercise.get('exerciseName')` — string
  - `exercise.get('sets')` — list of set dicts:
    - `s.get('setNumber')` — Decimal
    - `s.get('weight')` — Decimal or None
    - `s.get('reps')` — Decimal or None  
    - `s.get('rpe')` — Decimal or None

### Python csv.writer Handles Quoting Automatically

`csv.writer` with default dialect (excel) correctly quotes fields containing commas, quotes, or newlines. The output is RFC 4180 compliant and opens correctly in Excel and Google Sheets (NFR24).

### Empty Export

If user has no sessions, CSV should still return headers-only (not an empty file or error). The `generate_csv([])` call produces:
```
date,sport,exercise,set,weight,reps,rpe,notes\r\n
```
This opens correctly in Excel (shows column headers with no rows).

---

## Dev Agent Record

### Implementation Notes

- Created `export_service.py` with `_to_num()` for Decimal→int/float conversion and `generate_csv()` producing RFC 4180 CSV with one row per set; notes appear only on the first set row of each session.
- Created `export.py` router: thin `POST /export` endpoint using `get_current_user` dependency, delegates to `session_service.get_sessions()` and `export_service.generate_csv()`, returns `fastapi.Response` with `text/csv` media type and `Content-Disposition` header.
- Registered `export_router` in `main.py` after `feedback_router`.
- Added `exportTrainingData()` to `api.js` using raw `fetch` (not `apiFetch`) to retrieve a Blob and trigger browser download via `URL.createObjectURL`.
- Updated `Profile.jsx`: added `exporting`/`exportError` state, `handleExport` handler, and a "Your data" section with secondary-style export button showing "Preparing your export..." during the request and inline red error on failure.
- All 5 new tests and 17 regression tests pass (22 total).

### Completion Notes

✅ All 7 tasks and all subtasks complete. 22/22 tests pass. All ACs satisfied: CSV export via POST /export (AC1), RFC 4180 compliant output (AC2), "Preparing your export..." inline UX (AC3).

## File List

Created:
- backend/services/export_service.py
- backend/routers/export.py
- backend/tests/test_export.py

Modified:
- backend/main.py
- frontend/src/api.js
- frontend/src/pages/Profile.jsx

## Change Log

- 2026-04-26: Story 5.2 created — Training Data Export. Adds POST /export endpoint, CSV generation service, browser download in Profile UI.
- 2026-04-26: Story 5.2 implemented — all tasks complete, 22 tests passing, status set to review.
