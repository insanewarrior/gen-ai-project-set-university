# Story 2.3: Session History & Detail View

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **athlete**,
I want to view my training history and drill into individual sessions,
So that I can review past training and track my progress over time.

## Acceptance Criteria

1. **Given** I navigate to the History tab **When** the page loads **Then** I see my training sessions in reverse chronological order, displayed as borderless date-grouped rows with monospace set counts right-aligned (D6 minimal style per UX-DR12 History variant) **And** the page loads within 2 seconds for up to 500 sessions (NFR3)

2. **Given** I have sessions in my history **When** I tap on a session row **Then** I see the full session detail: date, sport, each exercise with all sets (weight/reps/RPE), and notes (FR7)

3. **Given** I have no logged sessions **When** I navigate to the History tab **Then** I see the empty state: "No sessions logged yet." with a "Log Session" link to `/log` (UX-DR23)

4. **Given** the Dashboard/Home tab **When** I view my dashboard **Then** I see recent session cards (Dashboard variant: Zinc-800 background, 8px radius, showing sport tag, exercise count, total sets) and a prominent "Log Session" primary button (UX-DR12 Dashboard variant)

5. **Given** I am a new user with 0 sessions **When** I view the Dashboard **Then** I see: "Welcome to StrengthWise" heading, "Log your first session to get started." body text, primary "Log Session" button, and a chat input hint "Log a few sessions first, then ask me anything." (UX-DR23)

6. **Given** the backend has sessions for my user **When** I call `GET /sessions` **Then** sessions are returned sorted by date descending, queried efficiently by userId PK (NFR17)

7. **Given** the backend **When** I call `GET /sessions/{id}?sessionDate=...` **Then** I receive the full session record including all exercises, sets, and notes

## Tasks / Subtasks

- [x] Task 1: Create SessionCard component (AC: #1, #4)
  - [x] 1.1: Create `frontend/src/components/SessionCard.jsx`
  - [x] 1.2: Props: `session: object`, `variant: "dashboard" | "history"`, `onClick: () => void`
  - [x] 1.3: **Dashboard variant:** Zinc-800 background, `rounded-lg` (8px radius), `p-3` padding. Show: date (formatted e.g. "Apr 25, 2026"), sport tag (e.g. "Grip Sport" in small Zinc-400 text), exercise count ("4 exercises"), total set count ("12 sets"). Use `cursor-pointer hover:bg-zinc-700` for tap interaction.
  - [x] 1.4: **History variant:** Borderless (`bg-transparent`), bottom divider only (`border-b border-zinc-800`), `py-3 px-0`. Date left-aligned, monospace set count right-aligned (`font-mono text-zinc-400 text-sm`). Sport tag inline with date.
  - [x] 1.5: Date display helper: format `sessionDate` (ISO "YYYY-MM-DD") to readable format — use `new Date(date + 'T00:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })`
  - [x] 1.6: Compute exercise count: `session.exercises?.length || 0`
  - [x] 1.7: Compute total sets: `session.exercises?.reduce((sum, ex) => sum + (ex.sets?.length || 0), 0) || 0`
  - [x] 1.8: Sport display mapping: `{ grip: "Grip Sport", armwrestling: "Armwrestling", powerlifting: "Powerlifting", general: "General Strength" }`
  - [x] 1.9: Accessibility: `role="article"`, `aria-label="Training session: {date} - {sport}"`, `tabIndex={0}`, `onKeyDown` Enter triggers onClick
  - [x] 1.10: Touch target: entire row is tappable, minimum 44px height — `min-h-[44px]` ensures this

- [x] Task 2: Create SessionDetail component (AC: #2)
  - [x] 2.1: Create `frontend/src/components/SessionDetail.jsx`
  - [x] 2.2: Props: `session: object`, `onBack: () => void`
  - [x] 2.3: Header section: back arrow button (left arrow `←` or `<`) + date + sport tag
  - [x] 2.4: For each exercise in `session.exercises`: render exercise name as `text-zinc-100 font-semibold`, then a table/grid of sets below it
  - [x] 2.5: Sets display: 4-column grid matching SetEntryRow layout — `grid grid-cols-[40px_1fr_1fr_60px]`. Columns: Set#, Weight (kg), Reps, RPE. All read-only text (not inputs). Monospace font (`font-mono`) for numeric values.
  - [x] 2.6: Notes section: if `session.notes` exists, show in a `text-zinc-400 text-sm italic` block below exercises with "Notes:" label
  - [x] 2.7: Container: `bg-zinc-900` (page background), exercises each in `bg-zinc-800 rounded-lg p-3 mb-2` blocks (same as ExerciseBlock styling from Story 2.2)
  - [x] 2.8: Back button: `text-zinc-400 hover:text-zinc-100` with `aria-label="Back to history"`, minimum 44x44px touch target

- [x] Task 3: Implement History.jsx page (AC: #1, #2, #3)
  - [x] 3.1: Replace stub in `frontend/src/pages/History.jsx` with full implementation
  - [x] 3.2: State: `sessions` (array), `loading` (boolean), `error` (string|null), `selectedSession` (object|null)
  - [x] 3.3: On mount: call `getSessions()` via api.js, set `sessions` from `response.data.sessions`, handle errors
  - [x] 3.4: Loading state: render 4-5 skeleton rows — `div` elements with `bg-zinc-800 rounded h-12 mb-2 animate-pulse` (UX-DR14)
  - [x] 3.5: Empty state (sessions.length === 0 after load): centered "No sessions logged yet." text (`text-zinc-400`) + `<Link to="/log">` "Log Session" button (`bg-blue-500 text-white px-6 py-3 rounded-lg font-medium`)
  - [x] 3.6: **Session list view (selectedSession === null):** group sessions by date. Use a `Map<dateString, session[]>` or simple grouping. For each date group: render date header (`text-zinc-500 text-xs uppercase font-semibold tracking-wider mb-1 mt-4`), then SessionCard (history variant) for each session in that group.
  - [x] 3.7: **Date grouping logic:** Group by `session.sessionDate`. Display format: "Today", "Yesterday", or the formatted date. Sessions within a date group maintain their API order (already sorted newest first within same date by SK).
  - [x] 3.8: On SessionCard click: call `getSession(sessionId, sessionDate)` from api.js to fetch full details, set `selectedSession`
  - [x] 3.9: **Session detail view (selectedSession !== null):** render `<SessionDetail session={selectedSession} onBack={() => setSelectedSession(null)} />`
  - [x] 3.10: Accessibility: session list container has `role="list"`, each SessionCard wrapped in `role="listitem"`

- [x] Task 4: Implement Dashboard.jsx page (AC: #4, #5)
  - [x] 4.1: Replace stub in `frontend/src/pages/Dashboard.jsx` with full implementation
  - [x] 4.2: State: `sessions` (array), `loading` (boolean)
  - [x] 4.3: On mount: call `getSessions()`, take first 3 sessions for "recent sessions" display
  - [x] 4.4: **New user empty state (sessions.length === 0 after load):**
    - "Welcome to StrengthWise" heading (`text-2xl font-bold text-zinc-100`)
    - "Log your first session to get started." body (`text-zinc-400 mt-2`)
    - Primary "Log Session" button: `<Link to="/log">` styled as `bg-blue-500 text-white px-6 py-3 rounded-lg font-medium text-center block mt-4 w-full md:w-auto`
    - Chat hint: "Log a few sessions first, then ask me anything." in `text-zinc-500 text-sm mt-6`
  - [x] 4.5: **Returning user (sessions.length > 0):**
    - "Recent Sessions" heading
    - Up to 3 SessionCard components (dashboard variant) — tapping navigates to `/history` (use `useNavigate()`)
    - "View All" secondary link to `/history` if more than 3 sessions exist
    - Primary "Log Session" button (`<Link to="/log">`)
  - [x] 4.6: Loading state: skeleton cards — 2-3 `bg-zinc-800 rounded-lg h-24 mb-3 animate-pulse` blocks
  - [x] 4.7: No illustrations, no mascots — just clean text and CTAs per UX anti-patterns

- [x] Task 5: Add getSession to api.js (AC: #7)
  - [x] 5.1: Add `getSession(sessionId, sessionDate)` function to `frontend/src/api.js`
  - [x] 5.2: Implementation: `return apiFetch('/sessions/' + sessionId + '?sessionDate=' + sessionDate)`
  - [x] 5.3: Export alongside existing `getExercises`, `createSession`, `getSessions`

- [x] Task 6: Backend verification (AC: #6, #7)
  - [x] 6.1: Verify `GET /sessions` returns sessions sorted newest first (ScanIndexForward=False already implemented in Story 2.2)
  - [x] 6.2: Verify `GET /sessions/{id}?sessionDate=...` returns full session with exercises and notes
  - [x] 6.3: Verify response fields are camelCase: `sessionDate`, `exerciseId`, `exerciseName`, `sportType`, `setNumber`
  - [x] 6.4: **No new backend code needed** — `GET /sessions` and `GET /sessions/{id}` were fully implemented in Story 2.2 (session_service.py + sessions.py router). This story only consumes the existing endpoints.

- [x] Task 7: Frontend manual testing (AC: #1-#5)
  - [x] 7.1: Start local dev (`make dev` or `cd frontend && npm run dev` + backend)
  - [x] 7.2: With 0 sessions: verify Dashboard shows empty state, History shows empty state with "Log Session" link
  - [x] 7.3: Log 2-3 sessions via /log tab
  - [x] 7.4: History tab: sessions appear in reverse chronological order, date-grouped, borderless rows
  - [x] 7.5: Tap a session row in History → full detail view appears with all exercises, sets, notes
  - [x] 7.6: Back button in detail view → returns to session list
  - [x] 7.7: Dashboard: shows recent session cards (up to 3), "Log Session" button, "View All" link
  - [x] 7.8: Verify 44px minimum touch targets on all tappable elements
  - [x] 7.9: Verify keyboard navigation: Tab through session rows, Enter opens detail

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow these exactly:**

- **No new backend endpoints or services needed.** `GET /sessions` and `GET /sessions/{id}?sessionDate=...` are already implemented in `backend/routers/sessions.py` and `backend/services/session_service.py` from Story 2.2. This story is purely frontend.
- **Use existing `getSessions()` from api.js.** Already implemented in Story 2.2: `apiFetch('/sessions', {}, { redirectOn401: false })`. Returns `{ data: { sessions: [...] } }`.
- **Use existing `apiFetch()` for getSession.** New `getSession(sessionId, sessionDate)` follows the same pattern. Uses `GET /sessions/{id}?sessionDate=...` endpoint.
- **Thin pages, reusable components.** `SessionCard` and `SessionDetail` are separate component files per architecture component list. Pages (`History.jsx`, `Dashboard.jsx`) compose these components.
- **No state management libraries.** `useState` + `useEffect` + native `fetch` via api.js wrapper. No Redux, no Zustand, no Context for this.
- **React Router for navigation.** Use `<Link to="/log">` and `<Link to="/history">` for navigation links. Use `useNavigate()` for programmatic navigation from Dashboard card clicks.

### Existing Backend API Contract

**`GET /sessions` response (already working):**
```json
{
  "data": {
    "sessions": [
      {
        "userId": "test-user-001",
        "sk": "2026-04-25#uuid-here",
        "sessionId": "uuid-here",
        "sessionDate": "2026-04-25",
        "sport": "grip",
        "exercises": [
          {
            "exerciseId": "grip-gripper-close",
            "exerciseName": "Gripper Close",
            "sportType": "grip",
            "sets": [
              { "setNumber": 1, "weight": 80.0, "reps": 3, "rpe": 9.0 }
            ]
          }
        ],
        "notes": "Felt strong today",
        "createdAt": "2026-04-25T14:30:00Z"
      }
    ]
  }
}
```

**`GET /sessions/{id}?sessionDate=YYYY-MM-DD` response (already working):**
```json
{
  "data": {
    "session": { ... same shape as above ... }
  }
}
```

**Important field types from DynamoDB:**
- `weight` may be a `Decimal` type serialized as a number in JSON — handle as `Number` in JS
- `rpe` is optional (`null` if not provided)
- `notes` is optional (key may be absent if null)
- `exercises` is always an array (may be empty but shouldn't be per Story 2.2 validation)
- Sessions are sorted newest first by the backend (DynamoDB query with `ScanIndexForward=False`)

### Frontend Implementation Patterns

**SessionCard date formatting:**
```javascript
const SPORT_LABELS = {
  grip: 'Grip Sport',
  armwrestling: 'Armwrestling',
  powerlifting: 'Powerlifting',
  general: 'General Strength',
}

function formatDate(dateStr) {
  const today = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
  if (dateStr === today) return 'Today'
  if (dateStr === yesterday) return 'Yesterday'
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })
}
```

**History page date grouping:**
```javascript
function groupByDate(sessions) {
  const groups = new Map()
  sessions.forEach(s => {
    const date = s.sessionDate
    if (!groups.has(date)) groups.set(date, [])
    groups.get(date).push(s)
  })
  return groups // Map preserves insertion order; sessions already sorted newest first
}
```

**Dashboard session card click → navigate to History:**
```javascript
import { useNavigate, Link } from 'react-router-dom'

// In Dashboard component:
const navigate = useNavigate()

// On card click — navigate to history tab (detail view is within History page state)
<SessionCard
  session={session}
  variant="dashboard"
  onClick={() => navigate('/history')}
/>
```

**API call pattern (same as Stories 2.1 and 2.2):**
```javascript
const [sessions, setSessions] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)

useEffect(() => {
  async function load() {
    try {
      const result = await getSessions()
      setSessions(result.data.sessions || [])
    } catch (err) {
      setError('Failed to load sessions.')
    } finally {
      setLoading(false)
    }
  }
  load()
}, [])
```

### Styling Reference (from UX Design Spec)

**History variant (D6 Minimal Data-Forward):**
- Borderless session rows
- Date group headers: small, uppercase, zinc-500
- Monospace set counts right-aligned
- Bottom dividers only (1px Zinc-800)
- No card backgrounds — just content and dividers

**Dashboard variant (D1+D5 Card Style):**
- Zinc-800 background
- 8px border-radius (`rounded-lg`)
- 12px padding (`p-3`)
- Sport tag + exercise count + set count
- Cursor pointer + hover state

**Skeleton screens (UX-DR14):**
- Zinc-800 blocks with pulse animation
- Match the shape of the content they replace
- `animate-pulse` Tailwind class

**Empty states (UX-DR23):**
- Clear text description
- Action link/button
- No illustrations, no mascots

**Dark theme tokens:**
- Background: `bg-zinc-900` (page level)
- Surface: `bg-zinc-800` (cards, blocks)
- Text primary: `text-zinc-100`
- Text secondary: `text-zinc-400`
- Text muted: `text-zinc-500`
- Primary action: `bg-blue-500 text-white`
- Border: `border-zinc-800` or `border-zinc-700`

### File Structure

Files this story creates or modifies:
```
frontend/src/
├── components/
│   ├── SessionCard.jsx          # NEW — dual-variant session summary display
│   └── SessionDetail.jsx        # NEW — full session detail with exercises/sets/notes
├── pages/
│   ├── History.jsx              # MODIFY (was stub) — session list + detail view
│   └── Dashboard.jsx            # MODIFY (was stub) — recent sessions + empty state
└── api.js                       # MODIFY — add getSession()
```

**NOT created or modified in this story:**
- No backend changes — all endpoints exist from Story 2.2
- No new tests — existing backend tests cover the API; frontend is tested manually
- `App.jsx` — routing to `/history` and `/` already exists, no changes needed
- `SessionCard` and `SessionDetail` are new components per architecture component list
- No changes to `TabBar.jsx`, `HeaderBar.jsx`, or any other existing components

**Files from Story 2.2 used but NOT modified:**
- `frontend/src/api.js` — `getSessions()` already exists; only add `getSession()`
- `backend/routers/sessions.py` — `GET /sessions` and `GET /sessions/{id}` already working
- `backend/services/session_service.py` — `get_sessions()` and `get_session()` already working

### Testing Requirements

**Frontend (manual — no Vitest required for this story):**
- History tab with 0 sessions → "No sessions logged yet." + "Log Session" link
- History tab with sessions → date-grouped list, newest first, borderless rows
- Tap session row → detail view loads with correct date, sport, exercises, sets, notes
- Back button in detail → returns to list without re-fetching (sessions still in state)
- Dashboard with 0 sessions → welcome empty state with "Log Session" button
- Dashboard with sessions → up to 3 recent cards, "View All" link to history
- Dashboard card tap → navigates to /history
- Responsive: verify on 375px mobile viewport — touch targets, single column layout
- Skeleton loading states visible during API fetch

**Backend (no new tests needed):**
- Story 2.2 already has tests for `GET /sessions` and `GET /sessions/{id}` — verify they still pass with `pytest backend/tests/`

### Previous Story Intelligence (Stories 2.1 and 2.2)

**From Story 2.2 (Training Session Logging Form):**
- `api.js` already has `getSessions()` and `createSession()` — follow same import/export pattern for `getSession()`
- `apiFetch()` wrapper handles JWT attachment, 401 redirect, and JSON parsing
- DynamoDB `Decimal` type: Story 2.2 had a debug issue with float→Decimal conversion. The `weight` and `rpe` fields in session responses may come back as numbers from DynamoDB through the API. Frontend receives them as normal JS numbers — no special handling needed.
- `ExerciseBlock` component uses `bg-zinc-800 rounded-lg p-3 mb-2` styling — reuse same styling for exercise display in SessionDetail
- Session payload structure confirmed: `exercises[]` with `exerciseId`, `exerciseName`, `sportType`, `sets[]` with `setNumber`, `weight`, `reps`, `rpe`

**From Story 2.1 (Exercise Database & Sport Selection):**
- Sport key mapping: `grip` → "Grip Sport", `armwrestling` → "Armwrestling", etc. — reuse same mapping in SessionCard display
- `getSavedSport()` from `SportSelector.jsx` — not needed for this story (History doesn't filter by sport)

**Git intelligence (recent commits):**
- `439e2be completed story 2-2` — last commit, all 2.2 files present and working
- Commit pattern: simple descriptive messages, no conventional commit format required
- No CI/CD pipeline — manual deploy only

### Anti-Patterns to Avoid

- **DO NOT** create new backend endpoints — `GET /sessions` and `GET /sessions/{id}` already exist and work.
- **DO NOT** add pagination to the sessions endpoint — per architecture, up to 500 sessions without pagination is acceptable for MVP (NFR3).
- **DO NOT** store selected session in URL params for detail view — keep it in component state within History.jsx. Deep linking to session detail is a post-MVP enhancement.
- **DO NOT** add a state management library — `useState` is sufficient for two independent pages.
- **DO NOT** create a separate route for session detail in App.jsx — the detail view lives within the History page as local state (selectedSession).
- **DO NOT** re-fetch sessions when navigating back from detail view — keep sessions in state, just clear selectedSession.
- **DO NOT** modify App.jsx routing — `/` and `/history` routes already point to Dashboard and History.
- **DO NOT** use `useEffect` with dependencies on `sessions` to trigger side effects — fetch once on mount only.
- **DO NOT** add filtering or search to the history page — that's post-MVP scope.
- **DO NOT** add illustrations or decorative elements to empty states — text + button only per UX anti-patterns.

### Project Structure Notes

- `frontend/src/components/SessionCard.jsx` and `SessionDetail.jsx` are new files per the architecture component list
- `frontend/src/pages/History.jsx` and `Dashboard.jsx` are stubs being replaced — they already exist with placeholder content
- `frontend/src/api.js` is modified to add one function — maintain all existing exports
- No new npm packages needed — React, React Router, and Tailwind already installed

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.3] — Acceptance criteria, FR6, FR7, UX-DR12, UX-DR23, NFR3, NFR17
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture] — Sessions table: PK=userId, SK=sessionDate#sessionId; query with ScanIndexForward=False for newest first
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture] — useState + fetch, React Router v7, api.js wrapper, no state management library
- [Source: _bmad-output/planning-artifacts/architecture.md#Naming Patterns] — camelCase JSON fields, PascalCase React components, camelCase JS variables
- [Source: _bmad-output/planning-artifacts/architecture.md#Service Boundaries] — session_service owns Sessions table; GET /sessions and GET /sessions/{id} already mapped
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Session Card] — Dashboard variant (Zinc-800, 8px radius, sport tag + counts) and History variant (borderless, bottom-divider, monospace counts)
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design Direction] — D6 Minimal for History, D1+D5 Card for Dashboard
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Empty States] — Dashboard (welcome + log CTA), History (no sessions + log link)
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Loading States] — Skeleton screens with Zinc-800 pulse animation
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Accessibility] — role="article" for session cards, semantic HTML, 44px touch targets
- [Source: _bmad-output/implementation-artifacts/2-2-training-session-logging-form.md] — session_service, sessions router, DynamoDB schema, api.js functions, ExerciseBlock styling
- [Source: _bmad-output/implementation-artifacts/2-1-exercise-database-sport-selection.md] — sport key mapping, apiFetch pattern
- [Source: frontend/src/api.js] — existing apiFetch, getSessions, createSession, getExercises
- [Source: frontend/src/App.jsx] — existing routes: / → Dashboard, /history → History, /log → LogSession
- [Source: backend/routers/sessions.py] — GET /sessions and GET /sessions/{id}?sessionDate=... already implemented

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- Discovered `GET /sessions/{id}` uses snake_case query param `session_date` (not camelCase `sessionDate` as specified in story). Fixed `getSession()` in api.js to use `?session_date=` to match actual backend.
- ESLint flagged `react-refresh/only-export-components` when SessionCard.jsx exported both the component and utility functions. Extracted `formatDate` and `SPORT_LABELS` into a separate `sessionUtils.js` file.
- `moto` test dependency was not installed locally — installed it to run backend regression tests (22/22 passed).

### Completion Notes List

- Created `SessionCard` component with dual variants (dashboard: zinc-800 card with sport tag/counts; history: borderless rows with monospace set counts)
- Created `SessionDetail` component showing full session with exercises, sets grid (matching ExerciseBlock layout), and optional notes
- Replaced `History.jsx` stub with full implementation: loading skeletons, empty state with "Log Session" link, date-grouped session list, and inline detail view via `getSession()` API call
- Replaced `Dashboard.jsx` stub with full implementation: welcome empty state for new users (heading + body + CTA + chat hint), recent sessions (up to 3 cards) for returning users, "View All" link, "Log Session" button
- Added `getSession(sessionId, sessionDate)` to api.js using correct `session_date` query param
- All backend endpoints verified working (GET /sessions, GET /sessions/{id}?session_date=...)
- All 22 backend tests pass, 0 lint errors, frontend builds successfully
- Accessibility: `role="article"`, `aria-label`, `tabIndex={0}`, keyboard Enter navigation, 44px touch targets, `role="list"`/`role="listitem"` on session list

### File List

- frontend/src/components/SessionCard.jsx (NEW)
- frontend/src/components/SessionDetail.jsx (NEW)
- frontend/src/components/sessionUtils.js (NEW)
- frontend/src/pages/History.jsx (MODIFIED)
- frontend/src/pages/Dashboard.jsx (MODIFIED)
- frontend/src/api.js (MODIFIED)

### Change Log

- 2026-04-25: Implemented Story 2.3 — Session History & Detail View. Created SessionCard (dual variant), SessionDetail, and sessionUtils components. Replaced History and Dashboard page stubs with full implementations. Added getSession() to api.js. Fixed query param mismatch (sessionDate → session_date). All backend tests pass, lint clean, build succeeds.
