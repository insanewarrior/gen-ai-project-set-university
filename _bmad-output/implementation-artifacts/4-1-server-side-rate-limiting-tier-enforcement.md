# Story 4.1: Server-Side Rate Limiting & Tier Enforcement

Status: review

## Story

As a **system operator**,
I want per-user daily query limits enforced server-side with tier-based access,
so that LLM costs are bounded and the free tier is sustainable.

## Acceptance Criteria

1. **Given** a free-tier athlete (account older than 7 days) **When** they submit their 4th `/query` or `/analyze` request in a day **Then** the request is rejected with HTTP 429, error code "RATE_LIMIT_EXCEEDED", and detail including resetAt time and limit of 3 (FR15)

2. **Given** an athlete in their first 7 days (onboarding tier, detected via Cognito UserCreateDate) **When** they submit their 11th query in a day **Then** the request is rejected with HTTP 429 and a limit of 10 (FR16)

3. **Given** a premium-tier athlete **When** they submit queries **Then** they are not subject to daily limits but are still subject to per-minute burst rate limits of 10 queries/minute (FR17)

4. **Given** a `/query` or `/analyze` request **When** the rate_limit_service checks the QueryUsage DynamoDB table **Then** it uses atomic DynamoDB `UpdateItem` with condition expression — no race conditions, server-side enforced, cannot be bypassed by client manipulation (FR33, NFR12)

5. **Given** any rate limit check **When** the daily counter is read and incremented **Then** the operation uses the QueryUsage table (PK: userId, SK: date) and returns the current count for inclusion in the API response

## Critical Bug to Fix FIRST

**`_FREE_TIER_LIMIT = 20` in `backend/services/rate_limit_service.py` line 8 must be changed to `3`.**

This is a spec violation (FR15: "3 AI queries/day"). This single change will also fix the 2 pre-existing test failures in `backend/tests/test_rate_limit.py` — `test_first_query_allowed` expects `queries_remaining == 2` (limit 3 - 1 used) and `test_limit_enforced_on_4th_free_tier` expects 4th call to be denied.

## What Already Exists — DO NOT RECREATE

**`backend/services/rate_limit_service.py`** — EXTEND ONLY:
- `check_and_increment(user_id: str, user_create_date: str | None = None) -> dict` — complete atomic DynamoDB logic with conditional update
- `_get_table()` — DynamoDB connection helper using `config.DYNAMODB_ENDPOINT`
- `_next_midnight()` — returns ISO 8601 reset time
- `_ONBOARDING_LIMIT = 10` and `_ONBOARDING_DAYS = 7` — correct
- `_FREE_TIER_LIMIT = 20` — **WRONG, change to 3**

**`backend/middleware/auth.py`** — EXTEND ONLY:
- `get_current_user()` — FastAPI dependency returning `str` (user_id only)
- `CurrentUser = str` — type alias used across all routers
- Cognito JWT verification with JWKS caching
- `AUTH_BYPASS` mode returning `config.TEST_USER_ID`

**`backend/routers/query.py`** and **`backend/routers/analyze.py`** — MINIMAL CHANGES ONLY:
- Both already call `rate_limit_service.check_and_increment(current_user)` (without `user_create_date`)
- Both handle 429 responses correctly
- Change ONLY the `check_and_increment` call to pass tier context

**`backend/tests/test_rate_limit.py`** — 3 tests already cover: first query allowed, 4th free-tier denied, reset_at format. They will PASS once `_FREE_TIER_LIMIT` is fixed to 3.

## Tasks / Subtasks

- [x] Task 1: Fix `_FREE_TIER_LIMIT` bug in `backend/services/rate_limit_service.py` (AC: #1, #5)
  - [x] 1.1: Change line 8: `_FREE_TIER_LIMIT = 20` → `_FREE_TIER_LIMIT = 3`
  - [x] 1.2: Run `pytest backend/tests/test_rate_limit.py` — all 3 tests must now pass
  - [x] 1.3: DO NOT change `_ONBOARDING_LIMIT = 10` or `_ONBOARDING_DAYS = 7` — they are correct

- [x] Task 2: Add premium tier detection to `backend/services/rate_limit_service.py` (AC: #3, #4)
  - [x] 2.1: Add constant at top of file alongside existing constants:
    ```python
    _PREMIUM_BURST_LIMIT = 10  # queries per minute for premium users
    ```
  - [x] 2.2: Add `is_premium` parameter to `check_and_increment`:
    ```python
    def check_and_increment(
        user_id: str,
        user_create_date: str | None = None,
        is_premium: bool = False,
    ) -> dict:
    ```
  - [x] 2.3: For premium users, skip daily limit check entirely but enforce per-minute burst. Add burst check BEFORE the existing tier/daily logic:
    ```python
    if is_premium:
        return _check_burst(user_id)
    ```
  - [x] 2.4: Add private `_check_burst(user_id: str) -> dict` function. Use DynamoDB with SK = `burst:{minute_key}` where `minute_key = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")`. Use the same QueryUsage table with a different SK format to avoid a new table:
    ```python
    def _check_burst(user_id: str) -> dict:
        table = _get_table()
        minute_key = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
        try:
            response = table.update_item(
                Key={"userId": user_id, "date": f"burst:{minute_key}"},
                UpdateExpression="SET queryCount = if_not_exists(queryCount, :zero) + :one",
                ConditionExpression="attribute_not_exists(queryCount) OR queryCount < :limit",
                ExpressionAttributeValues={
                    ":zero": 0, ":one": 1, ":limit": _PREMIUM_BURST_LIMIT
                },
                ReturnValues="UPDATED_NEW",
            )
            new_count = int(response["Attributes"]["queryCount"])
            return {
                "allowed": True,
                "queries_remaining": -1,  # unlimited daily for premium
                "tier_limit": -1,         # -1 signals unlimited to frontend
                "reset_at": _next_minute(),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {"allowed": False, "queries_remaining": 0, "reset_at": _next_minute()}
            raise
    ```
  - [x] 2.5: Add `_next_minute()` helper alongside `_next_midnight()`:
    ```python
    def _next_minute() -> str:
        from datetime import timedelta
        dt = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=1)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    ```
  - [x] 2.6: `timedelta` is already imported at the top of the file — do NOT add a duplicate import inside `_next_minute()`; keep the import at module level

- [x] Task 3: Update `backend/middleware/auth.py` to extract tier context from JWT (AC: #2, #3)
  - [x] 3.1: Add a second dependency function `get_user_context` that returns a dict with `user_id`, `user_create_date`, and `is_premium`. Keep `get_current_user` unchanged — it's used by sessions, exercises, export, and account routers that don't need tier info.
  - [x] 3.2: Add `UserContext` TypedDict at the top of auth.py (after imports):
    ```python
    from typing import TypedDict
    
    class UserContext(TypedDict):
        user_id: str
        user_create_date: str | None  # ISO 8601 from Cognito, None if unavailable
        is_premium: bool
    ```
  - [x] 3.3: Add `get_user_context` dependency — extracts `cognito:groups` from JWT for premium detection. Cognito includes groups automatically in the ID token as `cognito:groups` claim (list of group names). UserCreateDate is NOT in the JWT; call Cognito Admin API:
    ```python
    async def get_user_context(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    ) -> UserContext:
        # AUTH_BYPASS mode
        if config.AUTH_BYPASS.lower() == "true":
            return UserContext(
                user_id=config.TEST_USER_ID,
                user_create_date=config.TEST_USER_CREATE_DATE,
                is_premium=config.TEST_IS_PREMIUM.lower() == "true",
            )
        
        if credentials is None:
            raise HTTPException(status_code=401, detail={"error": "Unauthorized", "code": "MISSING_TOKEN"})
        
        token = credentials.credentials
        try:
            jwks = _get_jwks()
            payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail={"error": "Unauthorized", "code": "INVALID_TOKEN"})
            
            groups: list[str] = payload.get("cognito:groups", []) or []
            is_premium = "premium" in groups
            
            # UserCreateDate is not in JWT — fetch from Cognito Admin API
            user_create_date = _get_user_create_date(user_id)
            
            return UserContext(user_id=user_id, user_create_date=user_create_date, is_premium=is_premium)
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail={"error": "Token expired", "code": "TOKEN_EXPIRED"})
        except JWTError:
            raise HTTPException(status_code=401, detail={"error": "Unauthorized", "code": "INVALID_TOKEN"})
    ```
  - [x] 3.4: Add `_get_user_create_date(user_id: str) -> str | None` — calls Cognito AdminGetUser. Returns ISO 8601 string or None on failure (graceful degradation = free tier):
    ```python
    def _get_user_create_date(user_id: str) -> str | None:
        try:
            client = boto3.client("cognito-idp", region_name=config.COGNITO_REGION)
            response = client.admin_get_user(
                UserPoolId=config.COGNITO_USER_POOL_ID,
                Username=user_id,
            )
            create_date = response.get("UserCreateDate")
            if create_date:
                return create_date.isoformat()
            return None
        except Exception:
            return None  # Fail open: treat as free tier
    ```
  - [x] 3.5: Add `import boto3` at the top of `auth.py` (it's already a dependency via the project)
  - [x] 3.6: Add new config values to `backend/config.py`:
    ```python
    TEST_USER_CREATE_DATE = os.getenv("TEST_USER_CREATE_DATE", "2025-01-01T00:00:00")  # old enough = free tier
    TEST_IS_PREMIUM = os.getenv("TEST_IS_PREMIUM", "false")
    ```
  - [x] 3.7: DO NOT change `get_current_user` or `CurrentUser = str` — those are used by 4 other routers that must not break
  - [x] 3.8: DO NOT change `_get_jwks()` or the JWKS caching logic

- [x] Task 4: Update `/query` and `/analyze` routers to use tier context (AC: #1, #2, #3, #4)
  - [x] 4.1: In `backend/routers/query.py`:
    - Import `get_user_context, UserContext` alongside existing imports:
      ```python
      from middleware.auth import CurrentUser, UserContext, get_current_user, get_user_context
      ```
    - Add `user_context: UserContext = Depends(get_user_context)` parameter to `create_query`
    - Update `check_and_increment` call:
      ```python
      rate_result = rate_limit_service.check_and_increment(
          user_context["user_id"],
          user_create_date=user_context["user_create_date"],
          is_premium=user_context["is_premium"],
      )
      ```
    - Update `rag_service.query` call: `rag_service.query(user_context["user_id"], sanitized)`
    - Keep `current_user: CurrentUser = Depends(get_current_user)` REMOVED — replace entirely with `user_context`
    - **Update the 429 error detail to match the actual tier limit** (not hardcoded 3):
      ```python
      "detail": {"resetAt": rate_result["reset_at"], "limit": rate_result.get("tier_limit", 3)},
      ```
  - [x] 4.2: Apply the IDENTICAL changes to `backend/routers/analyze.py` — same pattern, same imports
  - [x] 4.3: DO NOT change the route path, HTTP method, status codes, or response structure

- [x] Task 5: Write tests for new rate limiting behavior (AC: #1–#5)
  - [x] 5.1: Add to `backend/tests/test_rate_limit.py` (do NOT create a new file — extend the existing one):
    - `test_onboarding_tier_allows_10_queries` — call `check_and_increment` 10 times with a fresh `user_create_date` (today's date), assert all allowed; 11th call denied
    - `test_premium_user_skips_daily_limit` — call `check_and_increment` with `is_premium=True` 15 times; assert all `allowed=True` and `queries_remaining == -1`
    - `test_premium_burst_limit_enforced` — call `check_and_increment` with `is_premium=True` 11 times in same minute; first 10 allowed, 11th denied
    - `test_user_create_date_none_defaults_to_free_tier` — call with `user_create_date=None`; verify limit is 3
  - [x] 5.2: Use the same `mock_aws()` context manager and DynamoDB table fixture pattern as the existing tests — mirror exactly
  - [x] 5.3: For onboarding test, pass `user_create_date=datetime.utcnow().isoformat()` (today) to trigger 10-query limit
  - [x] 5.4: Import `from datetime import datetime` at the top of test file if not already present
  - [x] 5.5: Mock `services.rate_limit_service._FREE_TIER_LIMIT` or use real value — test against actual constants, not magic numbers

- [x] Task 6: Add integration tests for rate-limited endpoints (AC: #1, #4)
  - [x] 6.1: Add `backend/tests/test_rate_limit_integration.py` (NEW file) — tests the 429 response via FastAPI TestClient:
    - `test_query_returns_429_when_rate_limited` — mock `rate_limit_service.check_and_increment` to return `{"allowed": False, ...}`, POST to `/query`, assert 429
    - `test_analyze_returns_429_when_rate_limited` — same for `/analyze`
    - `test_query_passes_user_context_to_rate_limiter` — verify `check_and_increment` is called with correct `user_id`, `user_create_date`, `is_premium`
  - [x] 6.2: Use `_bypass_client` fixture from `conftest.py` (AUTH_BYPASS=true) — this keeps auth out of scope
  - [x] 6.3: Use `unittest.mock.patch` to mock `services.rate_limit_service.check_and_increment`

- [x] Task 7: Verify zero regressions
  - [x] 7.1: Run `pytest backend/tests/test_sessions.py` — must still pass (sessions router unchanged)
  - [x] 7.2: Run `pytest backend/tests/test_analyze.py` — must still pass (5 tests)
  - [x] 7.3: Run `pytest backend/tests/test_query.py` — must still pass
  - [x] 7.4: Run `pytest backend/tests/test_rate_limit.py` — all 3 existing + 4 new tests pass
  - [x] 7.5: `GET /exercises`, `GET /sessions`, `POST /sessions`, `GET /sessions/{id}` — confirm still using `get_current_user` (not `get_user_context`); routers for these endpoints must NOT be changed

## Dev Notes

### CRITICAL: Bug Fix Resolves Pre-Existing Test Failures

`_FREE_TIER_LIMIT = 20` was wrong from the start. The two pre-existing failures noted in Story 3.4's completion notes are:
- `test_first_query_allowed` expects `queries_remaining == 2` (3 - 1 = 2), but gets 19 (20 - 1)
- `test_limit_enforced_on_4th_free_tier` expects 4th call denied at limit 3, but limit is 20 so it allows it

Fix the constant first (Task 1) to unblock the test suite.

### CRITICAL: Two Separate Auth Dependencies — Use the Right One

`get_current_user` → returns `str` (user_id only) — used by: sessions, exercises, export, account routers. **DO NOT CHANGE THESE ROUTERS.**

`get_user_context` → returns `UserContext` (user_id + user_create_date + is_premium) — used by: query, analyze routers ONLY. **This is what Story 4.1 adds.**

Mixing these up will either break existing endpoints or cause circular import issues.

### CRITICAL: Cognito UserCreateDate Is NOT in the JWT

Cognito ID tokens include `cognito:groups` (group membership) and `sub` (user ID), but do NOT include `UserCreateDate`. You must call `cognito-idp:AdminGetUser` to get it. The `_get_user_create_date()` function adds ~50-100ms per query request — acceptable per NFR2 (10s total budget).

In AUTH_BYPASS mode: `config.TEST_USER_CREATE_DATE` defaults to `"2025-01-01T00:00:00"` (over 7 days ago = free tier). To test onboarding tier locally, set `TEST_USER_CREATE_DATE` to today's date in `.env`.

### Premium Tier via Cognito Groups

Cognito groups ARE in the JWT (`cognito:groups` claim, list of strings). Create a Cognito group named exactly `"premium"` in the CDK stack. Any user in this group gets `is_premium=True`. No Admin API call needed for premium detection.

**CDK addition required** (in `infra/stacks/strengthwise_stack.py`):
```python
premium_group = cognito.CfnUserPoolGroup(
    self, "PremiumGroup",
    user_pool_id=user_pool.user_pool_id,
    group_name="premium",
    description="Premium tier users with unlimited daily queries",
)
```

### Premium Burst Limit: DynamoDB SK Format

Burst items use SK = `burst:YYYY-MM-DDTHH:MM` (same QueryUsage table). These items accumulate but are small (one item per user per minute active). For production, add a TTL attribute. For MVP, leave without TTL — DynamoDB costs are negligible at capstone scale.

### DynamoDB Condition Expression: No Race Conditions

The existing `UpdateItem` pattern with `ConditionExpression="attribute_not_exists(queryCount) OR queryCount < :limit"` is atomic — no need for read-then-write. Do NOT replace this with a `get_item` + `put_item` pattern.

### AUTH_BYPASS Checklist

When `AUTH_BYPASS=true`, `get_user_context` must return a fully valid `UserContext` with no Cognito/DynamoDB calls. Add to `.env.example`:
```
TEST_USER_ID=test-user-001
TEST_USER_CREATE_DATE=2025-01-01T00:00:00
TEST_IS_PREMIUM=false
```

### Existing Router Signature Pattern

Current `query.py` and `analyze.py` use `current_user: CurrentUser = Depends(get_current_user)`. After this story, replace with `user_context: UserContext = Depends(get_user_context)`. All calls that use `current_user` as a string must become `user_context["user_id"]`.

### File Locations

Files to MODIFY:
```
backend/config.py                    ← ADD TEST_USER_CREATE_DATE, TEST_IS_PREMIUM
backend/services/rate_limit_service.py  ← FIX _FREE_TIER_LIMIT=3, ADD _check_burst(), is_premium param
backend/middleware/auth.py           ← ADD UserContext, get_user_context, _get_user_create_date
backend/routers/query.py             ← USE get_user_context, pass tier context to rate limiter
backend/routers/analyze.py           ← USE get_user_context, pass tier context to rate limiter
backend/tests/test_rate_limit.py     ← EXTEND with 4 new tests
infra/stacks/strengthwise_stack.py   ← ADD premium Cognito group
```

Files to CREATE:
```
backend/tests/test_rate_limit_integration.py  ← NEW: endpoint-level 429 tests
```

Files NOT to touch:
```
backend/routers/sessions.py
backend/routers/exercises.py
backend/services/rag_service.py
backend/services/session_service.py
backend/middleware/sanitize.py
backend/models/query_models.py
backend/models/session_models.py
backend/tests/test_sessions.py
backend/tests/test_analyze.py    (existing tests must still pass)
frontend/                        (no frontend changes — that's Story 4.2)
```

### Anti-Patterns to Avoid

- **DO NOT** change `get_current_user` or `CurrentUser = str` — 4 routers depend on it
- **DO NOT** use `read_item` + `put_item` for rate counting — use the existing atomic `update_item` pattern
- **DO NOT** create a new DynamoDB table for burst limiting — reuse QueryUsage with `burst:` SK prefix
- **DO NOT** hardcode `"limit": 3` in the 429 response — use `rate_result.get("tier_limit", 3)` to respect the actual tier limit
- **DO NOT** call `_get_user_create_date()` in `get_current_user` — it's only needed in `get_user_context` for rate-limited endpoints
- **DO NOT** add rate limiting to sessions, exercises, or profile routes — only `/query` and `/analyze`
- **DO NOT** modify CDK stack for anything other than adding the premium Cognito group

### Request/Response Contract (unchanged)

**429 response** (same format as before, just correct tier_limit):
```json
{
  "detail": {
    "error": "Daily query limit reached",
    "code": "RATE_LIMIT_EXCEEDED",
    "detail": {
      "resetAt": "2026-04-27T00:00:00Z",
      "limit": 3
    }
  }
}
```

**200 response** `queriesRemaining` field: `-1` for premium (unlimited), `N` for free/onboarding. Frontend Story 4.2 will handle displaying this.

### Git Intelligence (from recent commits)

Pattern from last 4 stories (3.1–3.4):
- Services are extended, not replaced
- New functions added below existing ones in same file
- Thin routers — all logic in services
- pytest uses `mock_aws()` from moto for DynamoDB mocking
- `importlib.reload(rate_limit_service)` pattern needed when monkeypatching `config` in tests (already done in existing test_rate_limit.py tests — follow exactly)
- Pre-existing test failures were never fixed mid-story — fix them as part of this story (Task 1)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Fixed `_FREE_TIER_LIMIT = 3` (was 20), resolving 2 pre-existing test failures in test_rate_limit.py
- Added `_PREMIUM_BURST_LIMIT = 10`, `_check_burst()`, `_next_minute()` to rate_limit_service.py; premium users bypass daily limits and hit per-minute burst cap via DynamoDB `burst:YYYY-MM-DDTHH:MM` SK pattern
- Added `UserContext` TypedDict, `get_user_context` dependency, and `_get_user_create_date()` to auth.py; `get_current_user` unchanged
- Added `TEST_USER_CREATE_DATE` and `TEST_IS_PREMIUM` to config.py
- Updated query.py and analyze.py to use `get_user_context`, pass tier context to rate limiter, and use `rate_result.get("tier_limit", 3)` in 429 and 200 responses
- Extended test_rate_limit.py with 4 new tests (onboarding 10-limit, premium daily skip, premium burst enforcement, None date defaults to free tier); 7/7 pass
- Created test_rate_limit_integration.py with 3 endpoint-level tests; all pass
- Added premium Cognito group to infra CDK stack
- 24 regression tests across sessions, analyze, query, rate_limit: 0 failures
- Note: `test_premium_user_skips_daily_limit` tests 5 calls (not 15 as spec stated) to stay under burst cap — the spec's "15 times" conflicts with the 10/min burst limit; 5 calls exceed the free daily limit of 3 and prove no daily cap is enforced on premium users

### File List

Created:
- backend/tests/test_rate_limit_integration.py

Modified:
- backend/config.py
- backend/services/rate_limit_service.py
- backend/middleware/auth.py
- backend/routers/query.py
- backend/routers/analyze.py
- backend/tests/test_rate_limit.py
- infra/stacks/strengthwise_stack.py

## Change Log

- 2026-04-26: Story 4.1 created — Server-Side Rate Limiting & Tier Enforcement. Fixes _FREE_TIER_LIMIT=3 bug. Adds UserContext auth dependency for tier-aware rate limiting (onboarding via Cognito AdminGetUser, premium via cognito:groups JWT claim). Premium burst limiting via DynamoDB burst:minute SK pattern.
