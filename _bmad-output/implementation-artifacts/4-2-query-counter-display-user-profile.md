# Story 4.2: Query Counter Display & User Profile

Status: review

## Story

As an **athlete**,
I want to see my remaining daily queries and my usage statistics,
so that I can manage my query budget and see how much I've used the system.

## Acceptance Criteria

1. **Given** I am using the Chat interface **When** I open the Chat tab (before submitting any query) **Then** I see a QueryCounter showing "X of Y queries remaining today" in the header area below the chat input (UX-DR9)

2. **Given** my query count is at 1 remaining **When** the QueryCounter renders **Then** it displays in Amber-400 text as a warning state (UX-DR9)

3. **Given** my daily limit is exhausted **When** I view the Chat interface **Then** the QueryCounter shows in Red-400 with reset time, the ChatInputBar is disabled with message "Daily limit reached. Resets at [time]." — no interstitial paywall (UX-DR9, UX-DR23)

4. **Given** I call `GET /profile` **When** the response returns **Then** it includes my usage statistics: total sessions logged, total queries made, current tier (`"free"` | `"onboarding"` | `"premium"`), account creation date (FR23)

5. **Given** I view the profile area **When** it renders **Then** I see my usage stats displayed clearly with session count and query count

## Critical Context: What Already Exists — DO NOT RECREATE

**`frontend/src/components/QueryCounter.jsx`** — EXISTS, DO NOT RECREATE:
```jsx
// Props: queriesRemaining (number), resetAt (ISO string), tierLimit (default 3)
// Color logic: 0 → Red-400, ≤2 → Amber-400, else Zinc-400
// Shows: "X of Y queries remaining today" or "Daily limit reached. Resets at HH:MM."
export default function QueryCounter({ queriesRemaining, resetAt, tierLimit = 3 }) { ... }
```

**`frontend/src/pages/Chat.jsx`** — EXISTS, only small additions needed:
- Already tracks `queriesRemaining`, `tierLimit`, `resetAt` state
- QueryCounter is rendered ONLY after first query (`queriesRemaining !== null`)
- **Gap to fix:** QueryCounter shows as null on page load — must call `getProfile()` on mount to populate initial value
- DO NOT refactor `submitQuery`, message rendering, or error handling

**`frontend/src/api.js`** — EXISTS, only add `getProfile()`:
- `postQuery()`, `postAnalyze()`, `getSessions()` already exist and must not change
- Pattern: `apiFetch('/profile')` following same pattern as `getSessions()`

**`backend/middleware/auth.py`** — EXISTS:
- `UserContext` TypedDict — `{ user_id, user_create_date, is_premium }`
- `get_user_context` dependency — USE THIS for `/profile` (needs tier detection)
- `get_current_user` dependency — returns str only, do NOT use for profile router

**`backend/services/rate_limit_service.py`** — EXISTS, one read-only function to ADD:
- `check_and_increment()` — NEVER call this in profile router (it increments the counter!)
- Add `get_today_count(user_id: str) -> int` — non-incrementing DynamoDB `get_item` read
- Tier constants exist: `_FREE_TIER_LIMIT=3`, `_ONBOARDING_LIMIT=10`, `_ONBOARDING_DAYS=7`

**`backend/services/session_service.py`** — EXISTS:
- `get_sessions(user_id)` returns full session list — use `len()` for total count
- Pattern for `get_total_session_count(user_id)`: query Sessions PK with `Select='COUNT'`

## Tasks / Subtasks

- [x] Task 1: Add `get_today_count()` to rate_limit_service.py (non-incrementing read)
  - [x] 1.1: Add below existing functions in `backend/services/rate_limit_service.py`:
    ```python
    def get_today_count(user_id: str) -> int:
        table = _get_table()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        response = table.get_item(Key={"userId": user_id, "date": today})
        item = response.get("Item")
        if item is None:
            return 0
        return int(item.get("queryCount", 0))
    ```
  - [x] 1.2: Verify `_get_table()` and `datetime` import already exist in that file — DO NOT add duplicates

- [x] Task 2: Create `backend/services/profile_service.py` (NEW FILE)
  - [x] 2.1: Create `backend/services/profile_service.py`:
    ```python
    from datetime import datetime, timedelta

    import boto3
    from boto3.dynamodb.conditions import Key

    import config
    import services.rate_limit_service as rate_limit_service


    def _get_sessions_table():
        kwargs = {'region_name': 'us-east-1'}
        if config.DYNAMODB_ENDPOINT:
            kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
            kwargs['aws_access_key_id'] = 'fake'
            kwargs['aws_secret_access_key'] = 'fake'
        dynamodb = boto3.resource('dynamodb', **kwargs)
        return dynamodb.Table(config.SESSIONS_TABLE_NAME)


    def _get_usage_table():
        kwargs = {'region_name': 'us-east-1'}
        if config.DYNAMODB_ENDPOINT:
            kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
            kwargs['aws_access_key_id'] = 'fake'
            kwargs['aws_secret_access_key'] = 'fake'
        dynamodb = boto3.resource('dynamodb', **kwargs)
        return dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)


    def get_total_session_count(user_id: str) -> int:
        response = _get_sessions_table().query(
            KeyConditionExpression=Key('userId').eq(user_id),
            Select='COUNT',
        )
        return response['Count']


    def get_total_query_count(user_id: str) -> int:
        """Sum all daily queryCount entries (exclude burst: SK prefix items)."""
        response = _get_usage_table().query(
            KeyConditionExpression=Key('userId').eq(user_id),
        )
        total = 0
        for item in response.get('Items', []):
            sk = item.get('date', '')
            if not sk.startswith('burst:'):
                total += int(item.get('queryCount', 0))
        return total


    _FREE_TIER = "free"
    _ONBOARDING_TIER = "onboarding"
    _PREMIUM_TIER = "premium"


    def resolve_tier(user_create_date: str | None, is_premium: bool) -> str:
        if is_premium:
            return _PREMIUM_TIER
        if user_create_date:
            try:
                created = datetime.fromisoformat(user_create_date.replace("Z", ""))
                if (datetime.utcnow() - created).days < 7:
                    return _ONBOARDING_TIER
            except (ValueError, AttributeError):
                pass
        return _FREE_TIER
    ```
  - [x] 2.2: Note the `_get_sessions_table()` and `_get_usage_table()` helpers use the SAME config pattern as `session_service.py` and `rate_limit_service.py` — do not invent new patterns.

- [x] Task 3: Create `backend/routers/profile.py` (NEW FILE)
  - [x] 3.1: Create `backend/routers/profile.py`:
    ```python
    from fastapi import APIRouter, Depends

    import services.profile_service as profile_service
    import services.rate_limit_service as rate_limit_service
    from middleware.auth import UserContext, get_user_context

    router = APIRouter(prefix="/profile", tags=["profile"])

    _TIER_LIMITS = {"free": 3, "onboarding": 10, "premium": -1}


    @router.get("")
    async def get_profile(user_context: UserContext = Depends(get_user_context)):
        user_id = user_context["user_id"]
        tier = profile_service.resolve_tier(
            user_context["user_create_date"],
            user_context["is_premium"],
        )
        tier_limit = _TIER_LIMITS[tier]

        today_count = rate_limit_service.get_today_count(user_id)
        if tier_limit == -1:
            queries_remaining = -1  # premium: unlimited
        else:
            queries_remaining = max(0, tier_limit - today_count)

        return {
            "data": {
                "totalSessions": profile_service.get_total_session_count(user_id),
                "totalQueries": profile_service.get_total_query_count(user_id),
                "tier": tier,
                "accountCreatedAt": user_context["user_create_date"],
                "queriesRemainingToday": queries_remaining,
                "tierLimit": tier_limit,
            }
        }
    ```
  - [x] 3.2: Use `get_user_context` NOT `get_current_user` — tier detection requires user_create_date and is_premium from UserContext

- [x] Task 4: Register profile router in `backend/main.py`
  - [x] 4.1: Add to imports:
    ```python
    from routers.profile import router as profile_router
    ```
  - [x] 4.2: Add after existing `app.include_router(analyze_router)`:
    ```python
    app.include_router(profile_router)
    ```

- [x] Task 5: Add `getProfile()` to `frontend/src/api.js`
  - [x] 5.1: Add after existing `getSession()` function:
    ```js
    export async function getProfile() {
      return apiFetch('/profile')
    }
    ```

- [x] Task 6: Update `frontend/src/pages/Chat.jsx` to show QueryCounter on mount
  - [x] 6.1: Add `getProfile` to the existing import line:
    ```js
    import { postQuery, postAnalyze, getSessions, getProfile } from '../api'
    ```
  - [x] 6.2: Add a mount effect AFTER the existing `getSessions` useEffect (NOT replacing it):
    ```js
    useEffect(() => {
      getProfile()
        .then(res => {
          const d = res.data
          setQueriesRemaining(d.queriesRemainingToday ?? null)
          if (d.tierLimit != null) setTierLimit(d.tierLimit)
        })
        .catch(() => {}) // non-critical: counter shows after first query if profile fails
    }, [])
    ```
  - [x] 6.3: DO NOT modify `submitQuery`, message rendering, QueryCounter render logic, or the existing `getSessions` useEffect — they already work correctly
  - [x] 6.4: DO NOT change `queriesRemaining` state name or the existing null-guard `if (queriesRemaining !== null)` before QueryCounter — that guard now fires on mount when profile loads

- [x] Task 7: Create `frontend/src/pages/Profile.jsx` (NEW FILE)
  - [x] 7.1: Create the profile page:
    ```jsx
    import { useState, useEffect } from 'react'
    import { getProfile } from '../api'
    import QueryCounter from '../components/QueryCounter'

    const TIER_LABELS = {
      free: 'Free',
      onboarding: 'Onboarding (10/day)',
      premium: 'Premium',
    }

    function StatRow({ label, value }) {
      return (
        <div className="flex justify-between items-center py-3 border-b border-zinc-700 last:border-0">
          <span className="text-zinc-400 text-sm">{label}</span>
          <span className="text-zinc-100 font-medium">{value}</span>
        </div>
      )
    }

    function formatDate(iso) {
      if (!iso) return '—'
      return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    }

    export default function Profile() {
      const [profile, setProfile] = useState(null)
      const [loading, setLoading] = useState(true)
      const [error, setError] = useState(null)

      useEffect(() => {
        getProfile()
          .then(res => setProfile(res.data))
          .catch(() => setError('Could not load profile.'))
          .finally(() => setLoading(false))
      }, [])

      if (loading) {
        return (
          <div className="flex flex-col gap-3 mt-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-zinc-800 rounded-lg h-10 animate-pulse" />
            ))}
          </div>
        )
      }

      if (error) {
        return <p className="text-red-400 text-sm mt-4">{error}</p>
      }

      return (
        <div>
          <div className="bg-zinc-800 rounded-lg px-4 mb-6">
            <StatRow label="Sessions logged" value={profile.totalSessions} />
            <StatRow label="Queries made" value={profile.totalQueries} />
            <StatRow label="Account tier" value={TIER_LABELS[profile.tier] ?? profile.tier} />
            <StatRow label="Member since" value={formatDate(profile.accountCreatedAt)} />
          </div>
          <div className="bg-zinc-800 rounded-lg px-4 py-3">
            <p className="text-zinc-400 text-xs mb-1">Today's query budget</p>
            <QueryCounter
              queriesRemaining={profile.queriesRemainingToday}
              tierLimit={profile.tierLimit}
            />
          </div>
        </div>
      )
    }
    ```

- [x] Task 8: Add `/profile` route in `frontend/src/App.jsx`
  - [x] 8.1: Add import alongside existing page imports:
    ```js
    import Profile from './pages/Profile'
    ```
  - [x] 8.2: Add to TITLES map:
    ```js
    '/profile': 'Profile',
    ```
  - [x] 8.3: Add route inside `AuthenticatedShell`'s Route children, BEFORE the wildcard redirect:
    ```jsx
    <Route path="/profile" element={<Profile />} />
    ```
  - [x] 8.4: DO NOT add a 5th tab — architecture specifies 4 tabs (Home, Log, Chat, History). Profile is accessible via link from Dashboard.

- [x] Task 9: Add Profile link to Dashboard
  - [x] 9.1: In `frontend/src/pages/Dashboard.jsx`, add a "View Profile" link in the returning-user section, below the "Log Session" button. Use a Ghost-style button (transparent, Zinc-400 text, per UX-DR18):
    ```jsx
    import { Link, useNavigate } from 'react-router-dom'
    // (Link is already imported)

    // Add below the existing "Log Session" Link:
    <Link
      to="/profile"
      className="text-zinc-400 hover:text-zinc-200 text-sm text-center block mt-2"
    >
      View Profile & Usage Stats
    </Link>
    ```

- [x] Task 10: Write backend tests
  - [x] 10.1: Create `backend/tests/test_profile.py` (NEW FILE):
    - `test_profile_returns_200_with_stats` — mock `profile_service.get_total_session_count`, `profile_service.get_total_query_count`, `rate_limit_service.get_today_count`; assert response has `totalSessions`, `totalQueries`, `tier`, `accountCreatedAt`, `queriesRemainingToday`, `tierLimit`
    - `test_profile_free_tier_queries_remaining` — today_count=1, tierLimit=3, assert queriesRemainingToday=2
    - `test_profile_exhausted_queries` — today_count=3, tierLimit=3, assert queriesRemainingToday=0
    - `test_profile_premium_queries_remaining_is_minus_one` — is_premium=True, assert queriesRemainingToday=-1 and tierLimit=-1
    - `test_profile_requires_auth` — no bypass, assert 401
  - [x] 10.2: Use `_bypass_client(monkeypatch)` pattern from `test_query.py` (auth bypass via `monkeypatch.setattr(config, "AUTH_BYPASS", "true")`)
  - [x] 10.3: Use `unittest.mock.patch` to mock the service functions — do NOT set up real DynamoDB
  - [x] 10.4: Mock path strings: `"services.profile_service.get_total_session_count"`, `"services.rate_limit_service.get_today_count"`, etc.

- [x] Task 11: Verify zero regressions
  - [x] 11.1: `pytest backend/tests/test_sessions.py` — must still pass
  - [x] 11.2: `pytest backend/tests/test_query.py` — must still pass
  - [x] 11.3: `pytest backend/tests/test_analyze.py` — must still pass
  - [x] 11.4: `pytest backend/tests/test_rate_limit.py` — must still pass (only added get_today_count, no changes to existing functions)
  - [x] 11.5: `pytest backend/tests/test_profile.py` — all new tests pass

## Dev Notes

### CRITICAL: Never Increment Counter in Profile Endpoint

`/profile` MUST use `rate_limit_service.get_today_count()` (Task 1), NOT `check_and_increment()`. Calling `check_and_increment()` would consume one of the user's daily queries just by viewing their profile — a serious regression.

### CRITICAL: Use `get_user_context`, NOT `get_current_user`

Profile endpoint needs `user_create_date` (for tier detection) and `is_premium`. These only come from `UserContext`. Using `get_current_user` (returns str only) would prevent tier computation. See the pattern in `query.py` — profile router follows the same pattern.

### CRITICAL: QueryCounter Component Already Exists

`frontend/src/components/QueryCounter.jsx` is fully implemented and correct. DO NOT create a new component. Just call it with the right props. It handles all color states (normal/amber/red) and the disabled-input message format already.

### Chat Page: QueryCounter Visibility Before First Query

Current state: `queriesRemaining` is `null` on mount; QueryCounter hidden until first query response.
Required state: QueryCounter visible when Chat opens.
Fix: mount `useEffect` calling `getProfile()` to set initial `queriesRemaining` + `tierLimit`. The catch block is intentional — if profile call fails, the counter stays hidden (null) and appears after the first query as before. Don't throw or show an error for this.

### Profile Response Contract

```json
{
  "data": {
    "totalSessions": 42,
    "totalQueries": 87,
    "tier": "free",
    "accountCreatedAt": "2025-01-01T00:00:00",
    "queriesRemainingToday": 2,
    "tierLimit": 3
  }
}
```

Premium users: `queriesRemainingToday: -1`, `tierLimit: -1` (frontend must handle -1 as "unlimited").

### QueryCounter with `queriesRemaining === -1`

The existing `QueryCounter` component renders `"X of Y queries remaining today"` — for premium (`-1 of -1`) this looks odd. Add a guard in `Profile.jsx` only:
```jsx
{profile.queriesRemainingToday !== -1 && (
  <QueryCounter queriesRemaining={profile.queriesRemainingToday} tierLimit={profile.tierLimit} />
)}
{profile.queriesRemainingToday === -1 && (
  <span className="text-xs text-zinc-400">Unlimited daily queries (Premium)</span>
)}
```
Do NOT modify `QueryCounter.jsx` itself — other callers (Chat.jsx) already handle this correctly or don't encounter `-1` for non-premium users.

### Total Query Count: Exclude Burst SK Entries

QueryUsage table contains two types of items:
- Daily: `SK = "YYYY-MM-DD"` (e.g., `"2026-04-26"`) — queryCount = daily total
- Burst: `SK = "burst:YYYY-MM-DDTHH:MM"` — queryCount = per-minute premium burst counter

`get_total_query_count()` MUST exclude `burst:` SK items. The `profile_service.py` code in Task 2 handles this correctly via `if not sk.startswith('burst:')`.

### No 5th Tab — Profile Access via Dashboard Link

Architecture specifies 4 tabs: Home, Log, Chat, History (UX-DR3). Adding a 5th tab would violate the architecture. Profile is accessible via "View Profile & Usage Stats" link from the Dashboard (Task 9). No changes to `TabBar.jsx`.

### File Structure

Files to CREATE:
```
backend/services/profile_service.py
backend/routers/profile.py
backend/tests/test_profile.py
frontend/src/pages/Profile.jsx
```

Files to MODIFY:
```
backend/services/rate_limit_service.py  ← ADD get_today_count()
backend/main.py                          ← REGISTER profile router
frontend/src/api.js                      ← ADD getProfile()
frontend/src/pages/Chat.jsx              ← ADD mount useEffect for initial counter
frontend/src/App.jsx                     ← ADD /profile route + Profile import + TITLES entry
frontend/src/pages/Dashboard.jsx         ← ADD "View Profile" link
```

Files NOT to touch:
```
frontend/src/components/QueryCounter.jsx   ← already works perfectly
frontend/src/components/TabBar.jsx         ← 4 tabs per architecture
backend/middleware/auth.py                 ← UserContext + get_user_context already exist
backend/routers/query.py                   ← not in scope
backend/routers/analyze.py                 ← not in scope
backend/services/rate_limit_service.py (existing functions) ← only ADD get_today_count
```

### Patterns from Previous Stories

- Thin routers: all logic in services, router validates input and calls service
- `get_user_context` used when tier or creation date is needed; `get_current_user` for simple auth
- `boto3.resource('dynamodb', **kwargs)` with `config.DYNAMODB_ENDPOINT` for local/prod parity — copy the `_get_table()` pattern exactly
- `Select='COUNT'` on DynamoDB query avoids fetching all item data for count operations
- Test pattern: `monkeypatch.setattr(config, "AUTH_BYPASS", "true")` + `patch("services.X.function")` + `TestClient(app)`
- All test files use `from main import app` after patching config

### Auth Bypass in Tests

`get_user_context` in AUTH_BYPASS mode returns:
```python
UserContext(
    user_id=config.TEST_USER_ID,          # "test-user-001"
    user_create_date=config.TEST_USER_CREATE_DATE,  # "2025-01-01T00:00:00" (free tier)
    is_premium=config.TEST_IS_PREMIUM.lower() == "true",  # False
)
```
So profile tests default to free tier behavior. To test premium: `monkeypatch.setattr(config, "TEST_IS_PREMIUM", "true")`.

## Dev Agent Record

### Agent Model Used
claude-sonnet-4-6

### Completion Notes List
- Added `get_today_count(user_id)` to `rate_limit_service.py` — non-incrementing DynamoDB `get_item` read using same `_get_table()` helper. Verified `datetime` import already present.
- Created `profile_service.py` with `get_total_session_count()` (DynamoDB COUNT query), `get_total_query_count()` (excludes `burst:` SK items), and `resolve_tier()` (free/onboarding/premium logic).
- Created `routers/profile.py` — thin router using `get_user_context` for tier/date/premium info; never calls `check_and_increment`.
- Registered `profile_router` in `main.py` after existing routers.
- Added `getProfile()` to `api.js` following existing `apiFetch` pattern.
- Updated `Chat.jsx`: added `getProfile` import and a mount `useEffect` that sets initial `queriesRemaining` + `tierLimit`; catch block silently fails so counter still shows after first query if profile call fails.
- Created `Profile.jsx` with loading skeleton, error state, stats table, and conditional QueryCounter (hides for premium `-1` case with "Unlimited daily queries (Premium)" text).
- Added `/profile` route + `Profile` import + `TITLES` entry in `App.jsx`. No 5th tab added.
- Added "View Profile & Usage Stats" ghost link in returning-user section of `Dashboard.jsx`.
- Created `test_profile.py` with 5 tests: 200 with stats, free tier remaining, exhausted queries, premium `-1`, and 401 without auth. All 29 tests (5 new + 24 existing) pass.

### File List
backend/services/rate_limit_service.py
backend/services/profile_service.py
backend/routers/profile.py
backend/main.py
backend/tests/test_profile.py
frontend/src/api.js
frontend/src/pages/Chat.jsx
frontend/src/pages/Profile.jsx
frontend/src/App.jsx
frontend/src/pages/Dashboard.jsx

## Change Log

- 2026-04-26: Story 4.2 created — Query Counter Display & User Profile. Adds GET /profile endpoint, Profile.jsx page, initial QueryCounter on Chat mount, and Dashboard profile link.
- 2026-04-26: Story 4.2 implemented — all 11 tasks complete. 5 new backend tests + 24 regressions pass (29 total).
