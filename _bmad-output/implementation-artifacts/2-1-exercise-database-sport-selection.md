# Story 2.1: Exercise Database & Sport Selection

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **athlete**,
I want to select my sport and see exercises specific to my discipline,
So that the app speaks my sport's language and I can log accurately.

## Acceptance Criteria

1. **Given** the backend is running **When** I call `GET /exercises` with no query parameter **Then** I receive the full exercise database organized by sport (all four sports with their respective exercises)

2. **Given** the backend is running **When** I call `GET /exercises?sportType=grip` **Then** I receive only grip sport exercises: gripper close, hub lift, pinch block, wrist curl, fat bar (and any others defined)

3. **Given** the exercise database **When** I inspect the available sports **Then** all four sports are covered: Grip Sport (gripper close, hub lift, pinch block, wrist curl, fat bar), Armwrestling (pronation, supination, side pressure, hook, cupping, table practice), Powerlifting (squat, bench press, deadlift, overhead press, barbell row, and accessories), General Strength (pull-up, dip, Romanian deadlift, face pull, and common exercises) **And** the database is a static JSON file loaded at startup, not a DynamoDB table (FR25)

4. **Given** the frontend logging form **When** I open the SportSelector component **Then** I see a segmented control with 4 options (Grip Sport, Armwrestling, Powerlifting, General Strength) with 48px height per option and 44x44px minimum touch targets (UX-DR10, UX-DR22)

5. **Given** I have selected a sport before **When** I open the logging form **Then** the SportSelector auto-selects my last-used sport (UX-DR13, persisted via localStorage key `sw_last_sport`)

6. **Given** I select a sport in the SportSelector **When** the ExercisePicker renders **Then** exercises are filtered by the selected sport and sorted by my usage frequency with recent exercises first (UX-DR11, frequency tracked via localStorage key `sw_exercise_frequency`)

## Tasks / Subtasks

- [x] Task 1: Create exercise database JSON (AC: #1, #2, #3)
  - [x] 1.1: Create `backend/data/exercises.json` — define all four sport exercise lists
  - [x] 1.2: Grip Sport entries: `{"id": "gripper-close", "name": "Gripper Close", "sportType": "grip"}` — include: gripper close, hub lift, pinch block, wrist curl, fat bar, blob lift, thick bar deadlift, plate pinch
  - [x] 1.3: Armwrestling entries: include pronation, supination, side pressure, hook, cupping, table practice, hammer curl, reverse curl, wrist extension
  - [x] 1.4: Powerlifting entries: include squat, bench press, deadlift, overhead press, barbell row, Romanian deadlift, pause squat, close-grip bench, deficit deadlift
  - [x] 1.5: General Strength entries: include pull-up, dip, push-up, face pull, lat pulldown, cable row, overhead press, farmer's carry, kettlebell swing
  - [x] 1.6: Each exercise object shape: `{"id": "<sport-abbrev>-<slug>", "name": "<Display Name>", "sportType": "<sport_key>"}` — use kebab-case IDs, sport_key is one of: `grip`, `armwrestling`, `powerlifting`, `general`
  - [x] 1.7: Organize the JSON as an object keyed by sportType: `{"grip": [...], "armwrestling": [...], "powerlifting": [...], "general": [...]}`

- [x] Task 2: Create Pydantic models for exercises (AC: #1, #2, #3)
  - [x] 2.1: Create `backend/models/exercise_models.py`
  - [x] 2.2: `Exercise` model: `id: str`, `name: str`, `sport_type: str` — with `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` so `sportType` is the JSON key (camelCase)
  - [x] 2.3: `ExercisesData` model: `exercises: dict[str, list[Exercise]]` — keyed by sport string, value is list of exercises
  - [x] 2.4: `ExercisesResponse` model wrapping the data field: `data: ExercisesData`
  - [x] 2.5: Import from `pydantic import BaseModel, ConfigDict` and `pydantic.alias_generators import to_camel` — same pattern as all other models in the project

- [x] Task 3: Create exercise service (AC: #1, #2, #3)
  - [x] 3.1: Create `backend/services/exercise_service.py`
  - [x] 3.2: Load exercises at module level: read `backend/data/exercises.json` using `Path(__file__).parent.parent / "data" / "exercises.json"` — loaded once at import/startup, held in memory
  - [x] 3.3: Implement `get_exercises(sport_type: str | None = None) -> dict[str, list[dict]]`:
    - If `sport_type` is None → return full dict `{"grip": [...], "armwrestling": [...], "powerlifting": [...], "general": [...]}`
    - If `sport_type` is provided → validate it's a known key; return `{sport_type: [...]}` or raise `ValueError` with message `"Unknown sportType: {sport_type}. Valid values: grip, armwrestling, powerlifting, general"`
  - [x] 3.4: Do NOT use DynamoDB for exercises — static JSON only (architecture decision)

- [x] Task 4: Create exercises router (AC: #1, #2)
  - [x] 4.1: Create `backend/routers/exercises.py`
  - [x] 4.2: `GET /exercises` endpoint with optional query param `sport_type: str | None = Query(None, alias="sportType")`
  - [x] 4.3: Add `Depends(get_current_user)` auth dependency — all endpoints require auth per NFR7 (exercise list is gated to logged-in users like all other app endpoints)
  - [x] 4.4: Router calls `exercise_service.get_exercises(sport_type)` — router stays thin (no business logic)
  - [x] 4.5: Return 200 with `ExercisesResponse` — format: `{"data": {"exercises": {...}}}`
  - [x] 4.6: On `ValueError` from service (unknown sportType) → return 400 with `{"error": "Invalid sportType", "code": "VALIDATION_ERROR", "detail": {"validValues": ["grip", "armwrestling", "powerlifting", "general"]}}`
  - [x] 4.7: Add `router = APIRouter(prefix="/exercises", tags=["exercises"])`

- [x] Task 5: Register router in main.py (AC: #1, #2)
  - [x] 5.1: In `backend/main.py`, import and include `exercises_router` from `routers/exercises.py`
  - [x] 5.2: Add `app.include_router(exercises_router)` — same pattern as other router registrations
  - [x] 5.3: Verify existing routes (`/health`, `/me`) are unaffected

- [x] Task 6: Backend tests (AC: #1, #2, #3)
  - [x] 6.1: Create `backend/tests/test_exercises.py`
  - [x] 6.2: Test `GET /exercises` with `AUTH_BYPASS=true` → 200, response has `data.exercises` with all four sport keys (grip, armwrestling, powerlifting, general)
  - [x] 6.3: Test `GET /exercises?sportType=grip` with `AUTH_BYPASS=true` → 200, response has `data.exercises` with only `grip` key, contains at least: gripper close, hub lift, pinch block, wrist curl, fat bar
  - [x] 6.4: Test `GET /exercises?sportType=armwrestling` → 200, response has only `armwrestling` key with pronation and supination entries
  - [x] 6.5: Test `GET /exercises?sportType=invalid` → 400 with `code: VALIDATION_ERROR`
  - [x] 6.6: Test `GET /exercises` without auth (AUTH_BYPASS=false, no token) → 401
  - [x] 6.7: Use `conftest.py` test client fixture (same as `test_auth.py` — `AUTH_BYPASS=true` for auth-passing tests)
  - [x] 6.8: Verify camelCase in JSON response: `"sportType"` not `"sport_type"` in exercise objects

- [x] Task 7: Create SportSelector component (AC: #4, #5)
  - [x] 7.1: Create `frontend/src/components/SportSelector.jsx`
  - [x] 7.2: Props: `value: string` (current sport key, e.g. `"grip"`), `onChange: (sportKey: string) => void`, `disabled?: boolean`
  - [x] 7.3: Render a segmented control: 4 button options in a row — `Grip Sport`, `Armwrestling`, `Powerlifting`, `General Strength`
  - [x] 7.4: Button-to-sport-key mapping: `{"Grip Sport": "grip", "Armwrestling": "armwrestling", "Powerlifting": "powerlifting", "General Strength": "general"}`
  - [x] 7.5: Styling — container: `flex w-full rounded-lg overflow-hidden border border-zinc-700`; each option: `flex-1 py-3 text-sm font-medium text-center cursor-pointer` (48px height = `py-3` + 22px text ≈ 48px total — verify renders to ≥48px)
  - [x] 7.6: Active state: `bg-blue-500 text-white`; inactive: `bg-zinc-800 text-zinc-400 hover:bg-zinc-700`
  - [x] 7.7: Accessibility: `role="radiogroup"` on container, `role="radio"` on each option, `aria-checked={isSelected}`, `aria-label="Select sport"` on container
  - [x] 7.8: Keyboard: Tab to focus group, arrow keys to navigate options, Enter/Space to select
  - [x] 7.9: Touch target: each option must have minimum 44x44px touch area — verify on mobile viewport (full-width, 4 options = ~25% each — on 375px screen each is ~88px wide ✓)
  - [x] 7.10: No default selection in the component itself — parent controls `value` (controlled component pattern)

- [x] Task 8: Create ExercisePicker component (AC: #6)
  - [x] 8.1: Create `frontend/src/components/ExercisePicker.jsx`
  - [x] 8.2: Props: `sportType: string`, `onSelect: (exercise: {id, name, sportType}) => void`, `selectedExerciseIds?: string[]` (to mark already-added exercises)
  - [x] 8.3: On mount and when `sportType` changes: call `api.getExercises(sportType)` to fetch sport-filtered exercises
  - [x] 8.4: Display exercises as a scrollable list — each row: exercise name (left), tap to select
  - [x] 8.5: Sorting: read `sw_exercise_frequency` from localStorage (JSON object `{exerciseId: count}`); sort exercises by frequency count descending, then alphabetically for ties. Zero-usage exercises appear last alphabetically.
  - [x] 8.6: When an exercise is tapped: call `onSelect(exercise)`, then increment its count in `sw_exercise_frequency` localStorage (`frequency[id] = (frequency[id] || 0) + 1`)
  - [x] 8.7: Already-selected exercises (IDs in `selectedExerciseIds`): show with checkmark icon or different style (e.g., `text-zinc-500 line-through`) to indicate already added
  - [x] 8.8: Loading state: show skeleton rows (3-4 Zinc-800 pulse blocks) while API call is in flight
  - [x] 8.9: Empty state: if no exercises returned (shouldn't happen with valid sportType), show "No exercises found."
  - [x] 8.10: Touch targets: each exercise row minimum 44px height — use `py-3 px-4` (12px vertical padding + 20px text ≈ 44px)
  - [x] 8.11: Container: Zinc-800 background, overflow-y-scroll, max-height suitable for logging form context (will be specified in Story 2.2 when wired into form)

- [x] Task 9: Add getExercises to api.js (AC: #6)
  - [x] 9.1: In `frontend/src/api.js`, add `getExercises(sportType = null)` function
  - [x] 9.2: Calls `apiFetch('/exercises' + (sportType ? '?sportType=' + sportType : ''))` — uses existing `apiFetch` wrapper that handles JWT auth
  - [x] 9.3: Returns `{ data: { exercises: { [sportType]: [...] } }, error: null }` on success, `{ data: null, error: { message, code } }` on failure
  - [x] 9.4: Export `getExercises` alongside existing exports

- [x] Task 10: Implement last-sport persistence (AC: #5)
  - [x] 10.1: Create a simple localStorage helper in SportSelector (or inline): `getSavedSport()` returns `localStorage.getItem('sw_last_sport')` or `null`; `saveSport(key)` sets `localStorage.setItem('sw_last_sport', key)`
  - [x] 10.2: SportSelector does NOT manage its own state — parent (LogSession.jsx in Story 2.2) reads saved sport via `getSavedSport()` on mount and passes as initial `value`
  - [x] 10.3: Parent calls `saveSport(key)` in the `onChange` handler when user selects a sport
  - [x] 10.4: Export `getSavedSport` and `saveSport` from SportSelector.jsx (named exports alongside default component) for parent use in Story 2.2

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow these patterns exactly:**

- **Exercise database is static JSON, never DynamoDB.** Do NOT create a DynamoDB table for exercises. Do NOT add exercises to the Sessions table. Load `exercises.json` at module import time in `exercise_service.py` — it's loaded once per Lambda cold start and served from memory (architecture decision).
- **Routers are thin.** `exercises.py` router: validate query param, call `exercise_service.get_exercises()`, return response. Zero business logic in the router.
- **camelCase JSON.** All JSON fields use camelCase via `alias_generator=to_camel`. The Python attribute `sport_type` maps to JSON key `sportType`. Verify this in tests with an assertion on the raw JSON string.
- **Standard error response format.** On 400 (unknown sportType), use: `{"error": "...", "code": "VALIDATION_ERROR", "detail": {...}}` — never ad-hoc error shapes.
- **Auth on all endpoints.** GET /exercises requires `Depends(get_current_user)`. Exercise data is not user-specific but the endpoint is gated per NFR7 ("No unauthenticated endpoints except health check").
- **Standard success response format.** Wrap in `{"data": {"exercises": {...}}}` — never return a bare array or bare dict.

### Exercise Data Specification

**Sport key values (must match these exactly):**

| Display Name     | API key         | sportType field |
|------------------|-----------------|-----------------|
| Grip Sport       | `grip`          | `"grip"`        |
| Armwrestling     | `armwrestling`  | `"armwrestling"`|
| Powerlifting     | `powerlifting`  | `"powerlifting"`|
| General Strength | `general`       | `"general"`     |

**Minimum exercise entries required per AC:**

- `grip`: gripper close, hub lift, pinch block, wrist curl, fat bar (+ blob lift, plate pinch, thick bar deadlift for depth)
- `armwrestling`: pronation, supination, side pressure, hook, cupping, table practice (+ hammer curl, reverse curl, wrist extension)
- `powerlifting`: squat, bench press, deadlift (+ overhead press, barbell row, pause squat, close-grip bench, deficit deadlift, good morning)
- `general`: pull-up, dip, push-up, face pull, lat pulldown, cable row, overhead press, Romanian deadlift, farmer's carry, kettlebell swing

**Exercise ID convention:** `{sportAbbrev}-{slug}` where slug is kebab-case. Examples: `grip-gripper-close`, `aw-pronation`, `pl-squat`, `gen-pull-up`

### Backend Implementation Patterns

**exercise_service.py loading pattern:**
```python
# backend/services/exercise_service.py
import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"

def _load_exercises() -> dict:
    with open(_DATA_PATH, "r") as f:
        return json.load(f)

# Loaded at import time — once per Lambda cold start / uvicorn startup
_EXERCISES: dict = _load_exercises()

_VALID_SPORT_TYPES = {"grip", "armwrestling", "powerlifting", "general"}

def get_exercises(sport_type: str | None = None) -> dict:
    if sport_type is None:
        return _EXERCISES
    if sport_type not in _VALID_SPORT_TYPES:
        raise ValueError(f"Unknown sportType: {sport_type}. Valid values: {', '.join(sorted(_VALID_SPORT_TYPES))}")
    return {sport_type: _EXERCISES.get(sport_type, [])}
```

**exercises.py router pattern:**
```python
# backend/routers/exercises.py
from fastapi import APIRouter, Depends, HTTPException, Query
from middleware.auth import get_current_user, CurrentUser
import services.exercise_service as exercise_service

router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.get("")
async def get_exercises(
    sport_type: str | None = Query(None, alias="sportType"),
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        exercises = exercise_service.get_exercises(sport_type)
        return {"data": {"exercises": exercises}}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": str(e), "code": "VALIDATION_ERROR", "detail": {"validValues": ["grip", "armwrestling", "powerlifting", "general"]}},
        )
```

**Pydantic model approach note:** The response is returned as a plain dict (`{"data": {"exercises": exercises}}`). FastAPI will serialize it directly. Formal Pydantic `ExercisesResponse` model is optional for this endpoint since the exercises dict is dynamically shaped (keyed by sport). Keeping it as a plain dict is acceptable for the simple structure here — consistent with architecture's "no over-engineering" principle.

### Frontend Implementation Patterns

**SportSelector.jsx segmented control pattern:**
```jsx
// frontend/src/components/SportSelector.jsx

const SPORTS = [
  { key: 'grip', label: 'Grip Sport' },
  { key: 'armwrestling', label: 'Armwrestling' },
  { key: 'powerlifting', label: 'Powerlifting' },
  { key: 'general', label: 'General Strength' },
];

export function getSavedSport() {
  return localStorage.getItem('sw_last_sport') || null;
}

export function saveSport(sportKey) {
  localStorage.setItem('sw_last_sport', sportKey);
}

export default function SportSelector({ value, onChange, disabled = false }) {
  return (
    <div
      role="radiogroup"
      aria-label="Select sport"
      className="flex w-full rounded-lg overflow-hidden border border-zinc-700"
    >
      {SPORTS.map((sport) => (
        <button
          key={sport.key}
          role="radio"
          aria-checked={value === sport.key}
          onClick={() => !disabled && onChange(sport.key)}
          disabled={disabled}
          className={`flex-1 py-3 text-sm font-medium text-center transition-colors
            ${value === sport.key
              ? 'bg-blue-500 text-white'
              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          {sport.label}
        </button>
      ))}
    </div>
  );
}
```

**ExercisePicker frequency sorting:**
```js
// Read frequency from localStorage
function getFrequency() {
  try {
    return JSON.parse(localStorage.getItem('sw_exercise_frequency') || '{}');
  } catch {
    return {};
  }
}

function incrementFrequency(exerciseId) {
  const freq = getFrequency();
  freq[exerciseId] = (freq[exerciseId] || 0) + 1;
  localStorage.setItem('sw_exercise_frequency', JSON.stringify(freq));
}

// Sort exercises by frequency descending, then alphabetically
function sortByFrequency(exercises, frequency) {
  return [...exercises].sort((a, b) => {
    const freqDiff = (frequency[b.id] || 0) - (frequency[a.id] || 0);
    if (freqDiff !== 0) return freqDiff;
    return a.name.localeCompare(b.name);
  });
}
```

**api.js addition:**
```js
// Add to frontend/src/api.js
export async function getExercises(sportType = null) {
  const url = sportType ? `/exercises?sportType=${sportType}` : '/exercises';
  return apiFetch(url);
}
```

### File Structure

Files this story creates or modifies:

```
backend/
├── data/
│   └── exercises.json             # NEW — static exercise database for all 4 sports
├── models/
│   └── exercise_models.py         # NEW — Exercise Pydantic model (if using formal model)
├── services/
│   └── exercise_service.py        # NEW — load exercises.json, filter by sport
├── routers/
│   └── exercises.py               # NEW — GET /exercises with optional sportType filter
├── main.py                        # MODIFY — include exercises_router
└── tests/
    └── test_exercises.py          # NEW — 7 test cases for exercise endpoint

frontend/src/
├── components/
│   ├── SportSelector.jsx          # NEW — segmented control for sport selection
│   └── ExercisePicker.jsx         # NEW — sport-filtered exercise list with frequency sort
└── api.js                         # MODIFY — add getExercises() function
```

**NOT created in this story:**
- `frontend/src/pages/LogSession.jsx` — this page wires SportSelector + ExercisePicker together; deferred to Story 2.2
- Any DynamoDB changes — exercises are static JSON only
- Any changes to existing auth, sessions, or health endpoints

### Testing Requirements

**Backend (pytest) — all with AUTH_BYPASS=true via conftest:**
- GET /exercises → 200, response body has keys `data.exercises.grip`, `data.exercises.armwrestling`, `data.exercises.powerlifting`, `data.exercises.general`
- GET /exercises?sportType=grip → 200, response body has only `data.exercises.grip`; assert exercise names include "Gripper Close", "Hub Lift", "Pinch Block", "Wrist Curl", "Fat Bar"
- GET /exercises?sportType=armwrestling → 200, assert "Pronation" and "Supination" in names
- GET /exercises?sportType=invalid → 400, `code == "VALIDATION_ERROR"`
- GET /exercises (no auth, AUTH_BYPASS=false) → 401
- Assert camelCase: `response.json()["data"]["exercises"]["grip"][0]["sportType"]` exists (not `sport_type`)
- Assert exercise list is non-empty for each sport

**Frontend (manual — no Vitest required for this story):**
- Open LogSession page (after Story 2.2) and verify SportSelector renders 4 options with correct labels
- Select "Grip Sport" → ExercisePicker shows grip exercises
- Select "Armwrestling" → ExercisePicker updates to armwrestling exercises
- Tap an exercise 3 times → it sorts to top on next sport switch and back
- Refresh page → last-used sport is auto-selected from localStorage

### UX Design Compliance

Per UX spec (UX-DR10, UX-DR11, UX-DR13, UX-DR22):

- **SportSelector layout:** Full-width segmented control, NOT a dropdown. 4 equal-width buttons in a row. Minimum 48px height per UX-DR10 spec.
- **Touch targets:** Each sport option must be ≥44x44px touch target. On a 375px mobile screen with 4 options, each option is ≥88px wide — passes automatically. Height must be ≥44px.
- **Auto-selection:** SportSelector auto-selects from `localStorage.getItem('sw_last_sport')` — no default is shown if null (user must pick on first use). This happens in the LogSession parent (Story 2.2), not in SportSelector itself.
- **ExercisePicker:** Shows sport-specific exercises (not all exercises). Sorted by usage frequency (localStorage-tracked). Recent/frequent exercises appear at the top — this is the "sport speaks your language" moment.
- **No illustrations:** Exercise list is text-only — sport-specific exercise names are the credibility signal (UX spec anti-pattern: no generic fitness imagery).
- **Dark theme:** Zinc-800 backgrounds, Zinc-400 inactive text, Blue-500 active selection — same as rest of app.

### Previous Story Intelligence

**From Story 1.3 (User Registration & Authentication):**
- `Depends(get_current_user)` is the standard pattern for all protected routes. Import from `middleware.auth`. `CurrentUser = str` (userId). This exercises router follows the exact same pattern.
- `backend/middleware/__init__.py` exists — exercises.py goes in `backend/routers/` (same as all other routers).
- `backend/main.py` currently has `/health` (public) and `/me` (auth-protected). Add exercises router with `app.include_router(exercises_router)`.
- `backend/tests/conftest.py` has the TestClient fixture and AUTH_BYPASS setup — test_exercises.py uses the identical pattern.
- `api.js` already has `apiFetch()` which attaches JWT automatically. `getExercises()` simply calls `apiFetch('/exercises')`.
- Auth middleware JWKS cache is module-level per Lambda instance — exercises.json loading follows the same module-level singleton pattern.

**From Story 1.1 (Project Scaffold):**
- Separate Python venvs for `backend/` and `infra/` — no new packages needed for this story (json and pathlib are stdlib).
- `backend/data/` directory already exists in the scaffold (architecture spec) — just add `exercises.json` to it.
- conftest.py TestClient uses `AUTH_BYPASS=true` — all backend tests that need a user context follow this pattern.

### Anti-Patterns to Avoid

- **DO NOT** put exercises in DynamoDB — static JSON only. This is a deliberate architecture decision (exercise data is operator-managed, never user-written, and too small to warrant a database).
- **DO NOT** call DynamoDB in exercise_service.py — zero AWS calls in this service.
- **DO NOT** add business logic to the exercises router — just call service, return result.
- **DO NOT** use snake_case in the JSON response — `"sportType"` not `"sport_type"`. Use `alias_generator=to_camel` or return plain dict (dict keys are already camelCase from the JSON file).
- **DO NOT** make the exercises JSON load on every request — load at module import time (cold start / startup) only.
- **DO NOT** add SportSelector state management to the component — it's a controlled component (parent owns state). SportSelector only fires `onChange` callback.
- **DO NOT** store exercise frequency in DynamoDB for this story — localStorage is sufficient and avoids adding DynamoDB reads to every logging flow.
- **DO NOT** build the full LogSession page in this story — only the reusable SportSelector and ExercisePicker components. LogSession page integration is Story 2.2.
- **DO NOT** hard-code exercise lists in Python — the single source of truth is `exercises.json`.

### Project Structure Notes

- `backend/data/` directory exists per Story 1.1 scaffold — confirmed in architecture project structure. Add `exercises.json` here.
- `backend/models/` directory exists per scaffold. Add `exercise_models.py` if using formal Pydantic model, or skip if returning plain dict (both approaches are valid — plain dict is simpler and sufficient).
- `backend/routers/` directory exists per scaffold. `exercises.py` joins `__init__.py` in that directory.
- `backend/services/` directory exists per scaffold. `exercise_service.py` joins `__init__.py`.
- `frontend/src/components/` directory exists per scaffold. `SportSelector.jsx` and `ExercisePicker.jsx` join `TabBar.jsx`, `HeaderBar.jsx`, etc.
- No new npm packages needed for frontend — plain React state, fetch (via api.js), and localStorage.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.1] — Acceptance criteria, FR2, FR3, FR25, UX-DR10, UX-DR11, UX-DR13
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture] — Exercise database: static JSON file, loaded at startup, served from memory. Not DynamoDB.
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries] — exercises.py router, exercise_service.py, exercise_models.py, backend/data/exercises.json locations; GET /exercises maps to exercises.py → exercise_service → None (static JSON)
- [Source: _bmad-output/planning-artifacts/architecture.md#Naming Patterns] — camelCase JSON API fields, alias_generator=to_camel, snake_case Python, PascalCase React components
- [Source: _bmad-output/planning-artifacts/architecture.md#Format Patterns] — Standard success response: `{"data": {...}}`, standard error: `{"error": "...", "code": "...", "detail": {...}}`
- [Source: _bmad-output/planning-artifacts/architecture.md#Enforcement Guidelines] — camelCase JSON, api.js wrapper for frontend fetches, thin routers, business logic in services
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy] — SportSelector (UX-DR10): segmented control, 4 options, 48px height; ExercisePicker (UX-DR11): frequency-sorted, sport-filtered
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation] — Zinc-800 bg, Blue-500 active, Zinc-400 inactive, 44x44px touch targets
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Responsive Design & Accessibility] — role="radiogroup", role="radio", aria-checked, 44px minimum touch targets
- [Source: _bmad-output/implementation-artifacts/1-3-user-registration-authentication.md#Dev Notes] — get_current_user dependency pattern, AUTH_BYPASS mode, conftest.py test pattern, api.js apiFetch wrapper

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation completed without issues.

### Completion Notes List

- Implemented all 10 tasks across backend (Python/FastAPI) and frontend (React).
- `exercises.json` static database: 4 sports, 8–10 exercises each, camelCase `sportType` field throughout.
- `exercise_service.py` loads JSON at module import (cold-start singleton pattern). No DynamoDB used.
- `exercises.py` router is thin: validates param → calls service → returns plain dict. 400 error uses standard `VALIDATION_ERROR` code.
- `main.py` updated with `app.include_router(exercises_router)`.
- Pydantic models created (`exercise_models.py`) with `alias_generator=to_camel`; router uses plain dict response (acceptable per Dev Notes "no over-engineering").
- Backend: 7 new tests, all pass. Full regression suite 15/15 green. camelCase assertion confirmed in test.
- `SportSelector.jsx`: controlled component with `role="radiogroup"`/`role="radio"` ARIA, `bg-blue-500` active, `py-3` for ≥48px height. Named exports `getSavedSport` + `saveSport` for Story 2.2 parent.
- `ExercisePicker.jsx`: fetches on mount + sportType change, sorts by `sw_exercise_frequency` localStorage, skeleton loading state, already-selected style with checkmark.
- `api.js`: `getExercises(sportType)` added using existing `apiFetch` wrapper.

### File List

- `backend/data/exercises.json` — NEW
- `backend/models/exercise_models.py` — NEW
- `backend/services/exercise_service.py` — NEW
- `backend/routers/exercises.py` — NEW
- `backend/tests/test_exercises.py` — NEW
- `backend/main.py` — MODIFIED (added exercises_router import + include)
- `frontend/src/components/SportSelector.jsx` — NEW
- `frontend/src/components/ExercisePicker.jsx` — NEW
- `frontend/src/api.js` — MODIFIED (added getExercises export)

## Change Log

- 2026-04-25: Story 2.1 implemented — static exercise database (4 sports), GET /exercises endpoint with sportType filter, backend tests (7/7 pass, 15/15 full suite), SportSelector segmented control, ExercisePicker with frequency sort, localStorage helpers for sport persistence (Date: 2026-04-25)
