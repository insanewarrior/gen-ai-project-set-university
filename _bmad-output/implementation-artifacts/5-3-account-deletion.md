# Story 5.3: Account Deletion

Status: review

## Story

As an **athlete**,
I want to delete my account and all associated data permanently,
So that I can exercise my right to data removal.

## Acceptance Criteria

1. **Given** I choose to delete my account **When** the confirmation UI appears **Then** I see an inline (not modal) confirmation: "Delete your account and all training data? This cannot be undone." with a Red-500 "Delete" button and a Ghost "Cancel" button (UX-DR26)

2. **Given** I confirm account deletion via `DELETE /account` **When** the deletion processes **Then** all my data is removed from all DynamoDB tables (Sessions, QueryUsage, Feedback) and my Cognito account is deleted (FR22), and data removal completes within 24 hours (NFR13)

3. **Given** my account has been deleted **When** I try to sign in **Then** authentication fails and I would need to create a new account

---

## Critical Context: What Already Exists — DO NOT RECREATE

**`get_current_user`** — EXISTS in `backend/middleware/auth.py`. Returns `CurrentUser = str` (userId). Use for account router (not `get_user_context` — no tier needed).

**`config.COGNITO_USER_POOL_ID`** and **`config.COGNITO_REGION`** — EXIST in `backend/config.py`. Use for Cognito deletion.

**`config.SESSIONS_TABLE_NAME`**, **`config.QUERY_USAGE_TABLE_NAME`**, **`config.FEEDBACK_TABLE_NAME`** — ALL EXIST in `backend/config.py`. Use directly.

**`config.DYNAMODB_ENDPOINT`** — EXISTS. Used by all services for local dev. Follow same `_get_*_table()` pattern as `session_service.py` and `feedback_service.py`.

**`backend/routers/account.py`** — DOES NOT EXIST yet, must be created.

**`backend/services/account_service.py`** — DOES NOT EXIST yet, must be created.

**`frontend/src/pages/Profile.jsx`** — EXISTS. Add account deletion UI here (inline confirmation, NOT a new page or modal).

**`frontend/src/api.js`** — EXISTS. Add `deleteAccount()`. NOTE: `apiFetch()` calls `response.json()` — the delete endpoint returns `{"deleted": true}` (200 JSON) so `apiFetch` CAN be used here (unlike export which returned CSV).

**`backend/main.py`** — EXISTS. Register `account_router` after `export_router`.

**`signOut`** — EXPORTED from `frontend/src/auth.js`. Import and call after successful deletion.

---

## Critical Design Decisions

### DynamoDB Deletion Strategy — Per-Table Key Structure

**Sessions table** (PK=`userId`, SK=`sk`):
```python
# Query all sessions for user, then batch-delete by (userId, sk) pairs
response = sessions_table.query(
    KeyConditionExpression=Key('userId').eq(user_id),
    ProjectionExpression='userId, sk',
)
with sessions_table.batch_writer() as batch:
    for item in response['Items']:
        batch.delete_item(Key={'userId': item['userId'], 'sk': item['sk']})
```

**QueryUsage table** (PK=`userId`, SK=`date`):
```python
# Query all usage records for user, then batch-delete by (userId, date) pairs
response = query_usage_table.query(
    KeyConditionExpression=Key('userId').eq(user_id),
    ProjectionExpression='userId, #d',
    ExpressionAttributeNames={'#d': 'date'},  # 'date' is a reserved word
)
with query_usage_table.batch_writer() as batch:
    for item in response['Items']:
        batch.delete_item(Key={'userId': item['userId'], 'date': item['date']})
```

**CRITICAL — `date` is a reserved word in DynamoDB:** Use ExpressionAttributeNames `{'#d': 'date'}` for ProjectionExpression on the QueryUsage table.

**Feedback table** (PK=`queryId`, no GSI on userId):
```python
# Scan with FilterExpression — userId is not a key, requires full scan with pagination
paginator_key = None
while True:
    scan_kwargs = {
        'FilterExpression': Attr('userId').eq(user_id),
        'ProjectionExpression': 'queryId',
    }
    if paginator_key:
        scan_kwargs['ExclusiveStartKey'] = paginator_key
    response = feedback_table.scan(**scan_kwargs)
    with feedback_table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'queryId': item['queryId']})
    paginator_key = response.get('LastEvaluatedKey')
    if not paginator_key:
        break
```

**NOTE:** Feedback scan is acceptable since account deletion is a rare operation. No GSI exists on the Feedback table — do not add one.

### Cognito Deletion — Use Sub as Username

`get_current_user` returns `sub` (the Cognito UUID). The `admin_delete_user` API accepts the sub directly as Username — same pattern already used by `_get_user_create_date` in `auth.py`:
```python
import boto3
import config

client = boto3.client('cognito-idp', region_name=config.COGNITO_REGION)
client.admin_delete_user(
    UserPoolId=config.COGNITO_USER_POOL_ID,
    Username=user_id,  # sub UUID works directly
)
```

### Deletion Order — DynamoDB First, Cognito Last

Delete DynamoDB data first, Cognito last. This ensures:
- If DynamoDB deletion fails → Cognito still intact → user can retry
- If Cognito deletion fails after DynamoDB success → user loses data but can't re-auth (acceptable for MVP — NFR13 allows 24h window)

### API Response — Return 200 JSON (NOT 204)

Return `{"deleted": True}` with 200 status. This lets `apiFetch` in the frontend work correctly (it calls `response.json()` — 204 empty body would throw). No Pydantic response model needed.

```python
from fastapi import APIRouter, Depends
from middleware.auth import CurrentUser, get_current_user
import services.account_service as account_service

router = APIRouter(prefix="/account", tags=["account"])

@router.delete("")
async def delete_account(
    current_user: CurrentUser = Depends(get_current_user),
):
    account_service.delete_account(current_user)
    return {"deleted": True}
```

### Complete account_service.py Implementation

```python
import boto3
from boto3.dynamodb.conditions import Key, Attr

import config


def _get_dynamodb(**kwargs):
    if config.DYNAMODB_ENDPOINT:
        kwargs.setdefault('endpoint_url', config.DYNAMODB_ENDPOINT)
        kwargs.setdefault('aws_access_key_id', 'fake')
        kwargs.setdefault('aws_secret_access_key', 'fake')
    kwargs.setdefault('region_name', 'us-east-1')
    return boto3.resource('dynamodb', **kwargs)


def delete_account(user_id: str) -> None:
    dynamodb = _get_dynamodb()

    # 1. Delete all Sessions
    sessions_table = dynamodb.Table(config.SESSIONS_TABLE_NAME)
    response = sessions_table.query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ProjectionExpression='userId, sk',
    )
    with sessions_table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'userId': item['userId'], 'sk': item['sk']})

    # 2. Delete all QueryUsage records
    query_usage_table = dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)
    response = query_usage_table.query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ProjectionExpression='userId, #d',
        ExpressionAttributeNames={'#d': 'date'},
    )
    with query_usage_table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'userId': item['userId'], 'date': item['date']})

    # 3. Delete all Feedback (scan — no GSI on userId)
    feedback_table = dynamodb.Table(config.FEEDBACK_TABLE_NAME)
    paginator_key = None
    while True:
        scan_kwargs = {
            'FilterExpression': Attr('userId').eq(user_id),
            'ProjectionExpression': 'queryId',
        }
        if paginator_key:
            scan_kwargs['ExclusiveStartKey'] = paginator_key
        response = feedback_table.scan(**scan_kwargs)
        with feedback_table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(Key={'queryId': item['queryId']})
        paginator_key = response.get('LastEvaluatedKey')
        if not paginator_key:
            break

    # 4. Delete Cognito user (last — so DynamoDB is clean if this fails)
    cognito = boto3.client('cognito-idp', region_name=config.COGNITO_REGION)
    cognito.admin_delete_user(
        UserPoolId=config.COGNITO_USER_POOL_ID,
        Username=user_id,
    )
```

### Frontend deleteAccount() — Uses apiFetch (NOT raw fetch)

Unlike `exportTrainingData`, the delete endpoint returns JSON — `apiFetch` works:
```js
export async function deleteAccount() {
  return apiFetch('/account', { method: 'DELETE' })
}
```

### Frontend UX — Inline Confirmation in Profile.jsx

The confirmation is inline (NOT a modal — UX-DR26). Add BELOW the "Your data" export section.

State needed:
```jsx
const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
const [deleting, setDeleting] = useState(false)
const [deleteError, setDeleteError] = useState(null)
```

Handler:
```jsx
async function handleDeleteAccount() {
  setDeleting(true)
  setDeleteError(null)
  try {
    await deleteAccount()
    signOut()
    window.location.href = '/login'
  } catch {
    setDeleteError('Account deletion failed. Please try again.')
    setDeleting(false)
  }
}
```

Render — add below the "Your data" section:
```jsx
<div className="bg-zinc-800 rounded-lg px-4 py-3 mt-4">
  <p className="text-zinc-400 text-xs mb-2">Danger zone</p>
  {!showDeleteConfirm ? (
    <button
      onClick={() => setShowDeleteConfirm(true)}
      className="w-full py-2 px-4 text-red-400 rounded-lg text-sm hover:bg-red-500/10 transition-colors"
    >
      Delete Account
    </button>
  ) : (
    <div>
      <p className="text-zinc-300 text-sm mb-3">
        Delete your account and all training data? This cannot be undone.
      </p>
      <div className="flex gap-2">
        <button
          onClick={handleDeleteAccount}
          disabled={deleting}
          className="flex-1 py-2 px-4 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
        <button
          onClick={() => { setShowDeleteConfirm(false); setDeleteError(null) }}
          disabled={deleting}
          className="flex-1 py-2 px-4 text-zinc-400 rounded-lg text-sm hover:bg-zinc-700 disabled:opacity-50 transition-colors"
        >
          Cancel
        </button>
      </div>
      {deleteError && <p className="text-red-400 text-xs mt-2">{deleteError}</p>}
    </div>
  )}
</div>
```

**UX notes:**
- Initial state: Ghost-style "Delete Account" button (red text, no border, no bg — UX-DR26/Ghost)
- Confirmation state: expands inline with message + Red-500 "Delete" button + Ghost "Cancel"
- During deletion: "Deleting..." label, button disabled
- On success: `signOut()` + redirect to `/login` — no toast needed (user leaves the page)
- Error shown inline below buttons (Red-400 text, UX-DR19)
- Do NOT use a modal

### Imports to add to Profile.jsx

```jsx
import { useState, useEffect } from 'react'
import { getProfile, exportTrainingData, deleteAccount } from '../api'
import { signOut } from '../auth'
import QueryCounter from '../components/QueryCounter'
```

`signOut` must be imported from `'../auth'` (already exported there). `deleteAccount` from `'../api'`.

---

## Tasks / Subtasks

- [x] Task 1: Create `backend/services/account_service.py` (NEW FILE)
  - [x] 1.1: Implement `_get_dynamodb()` helper following same pattern as other services (check `config.DYNAMODB_ENDPOINT`)
  - [x] 1.2: Implement `delete_account(user_id: str) -> None`
  - [x] 1.3: Delete Sessions — query by PK=userId, batch_writer to delete all (userId, sk) pairs
  - [x] 1.4: Delete QueryUsage — query by PK=userId, use ExpressionAttributeNames `{'#d': 'date'}` (reserved word), batch_writer to delete
  - [x] 1.5: Delete Feedback — scan with `Attr('userId').eq(user_id)`, handle pagination via LastEvaluatedKey, batch_writer to delete by queryId
  - [x] 1.6: Delete Cognito user — `admin_delete_user(UserPoolId=config.COGNITO_USER_POOL_ID, Username=user_id)` — LAST step

- [x] Task 2: Create `backend/routers/account.py` (NEW FILE)
  - [x] 2.1: `DELETE /account` with `get_current_user` dependency
  - [x] 2.2: Call `account_service.delete_account(current_user)`
  - [x] 2.3: Return `{"deleted": True}` (200 JSON — NOT 204, so apiFetch works on frontend)
  - [x] 2.4: No Pydantic request model needed

- [x] Task 3: Register account router in `backend/main.py`
  - [x] 3.1: Add `from routers.account import router as account_router`
  - [x] 3.2: Add `app.include_router(account_router)` after `app.include_router(export_router)`

- [x] Task 4: Add `deleteAccount()` to `frontend/src/api.js`
  - [x] 4.1: Add `export async function deleteAccount() { return apiFetch('/account', { method: 'DELETE' }) }`
  - [x] 4.2: Place near other account-related functions (after `exportTrainingData`)

- [x] Task 5: Update `frontend/src/pages/Profile.jsx`
  - [x] 5.1: Add `useState` for `showDeleteConfirm`, `deleting`, `deleteError`
  - [x] 5.2: Import `deleteAccount` from `'../api'` and `signOut` from `'../auth'`
  - [x] 5.3: Add `handleDeleteAccount` async function (see pattern above)
  - [x] 5.4: Add "Danger zone" section below the "Your data" export section (mt-4)
  - [x] 5.5: Conditional render: Ghost red "Delete Account" button OR inline confirmation with message + Red-500 "Delete" + Ghost "Cancel"
  - [x] 5.6: On success: call `signOut()` then `window.location.href = '/login'`
  - [x] 5.7: Show inline error below buttons if `deleteError` is set
  - [x] 5.8: DO NOT change existing state (`profile`, `loading`, `error`, `exporting`, `exportError`), stat rows, QueryCounter, or export section

- [x] Task 6: Write backend tests
  - [x] 6.1: Create `backend/tests/test_account.py` (NEW FILE)
    - `test_delete_account_returns_200` — bypass auth; mock all 3 DynamoDB tables + Cognito; DELETE `/account`; assert 200 and `{"deleted": True}`
    - `test_delete_account_requires_auth` — no bypass; DELETE `/account` without auth header; assert 401
    - `test_delete_account_calls_all_tables` — bypass auth; mock `account_service.delete_account`; assert it was called with `"test-user-001"`
    - `test_delete_account_deletes_sessions` — unit test: mock sessions_table with 2 items; call `account_service.delete_account`; assert batch delete called for both
    - `test_delete_account_deletes_cognito` — mock cognito client; assert `admin_delete_user` called with correct UserPoolId and Username
  - [x] 6.2: Use `_bypass_client(monkeypatch)` pattern from `test_feedback.py` / `test_export.py`
  - [x] 6.3: Use `autouse` aws_credentials fixture (same as all other test files)
  - [x] 6.4: Mock with `unittest.mock.patch("services.account_service.delete_account", return_value=None)` for router-level tests

- [x] Task 7: Verify zero regressions
  - [x] 7.1: `pytest backend/tests/test_sessions.py` — must still pass
  - [x] 7.2: `pytest backend/tests/test_feedback.py` — must still pass
  - [x] 7.3: `pytest backend/tests/test_export.py` — must still pass
  - [x] 7.4: `pytest backend/tests/test_account.py` — all new tests pass

---

## File Structure

Files to CREATE:
```
backend/services/account_service.py
backend/routers/account.py
backend/tests/test_account.py
```

Files to MODIFY:
```
backend/main.py                    ← REGISTER account_router (after export_router)
frontend/src/api.js                ← ADD deleteAccount()
frontend/src/pages/Profile.jsx     ← ADD danger zone section + inline confirmation
```

Files NOT to touch:
```
backend/services/session_service.py   ← get_sessions() not needed here; account_service queries directly
backend/services/feedback_service.py  ← no changes needed
backend/services/export_service.py    ← no changes needed
backend/middleware/auth.py            ← get_current_user already works
backend/config.py                     ← all needed vars already exist
frontend/src/auth.js                  ← signOut() already exported, no changes
```

---

## Patterns from Previous Stories

**`_bypass_client(monkeypatch)` test pattern** — identical to `test_feedback.py` and `test_export.py`:
```python
def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)
```

**`aws_credentials` autouse fixture** — same as all test files:
```python
@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
```

**Router structure** — thin router calling service (same as `feedback.py`, `export.py`):
```python
router = APIRouter(prefix="/account", tags=["account"])
@router.delete("") ...
```

**`_get_dynamodb()` pattern** — follows same local-dev-aware initialization as all other services.

**DynamoDB `batch_writer()`** — boto3 resource's batch_writer handles chunking (max 25 items/request) automatically; just call `batch.delete_item(Key={...})` in a loop.

---

## Dev Notes

### CRITICAL: `date` is a DynamoDB Reserved Word

When querying/projecting the QueryUsage table, `date` is a reserved keyword. Use:
```python
ExpressionAttributeNames={'#d': 'date'}
```
in ProjectionExpression. Failure to do this causes `ValidationException` from DynamoDB.

### CRITICAL: Feedback Has No GSI on userId

The Feedback table PK is `queryId` — there is NO secondary index on `userId`. The only way to find all feedback for a user is a full table Scan with FilterExpression. This is fine for an infrequent deletion operation; do NOT add a GSI or change the table schema.

### CRITICAL: Scan Pagination

DynamoDB Scan returns at most 1 MB of data per call. Always handle `LastEvaluatedKey` in the Feedback scan loop. The implementation pattern above handles this correctly.

### CRITICAL: Cognito `admin_delete_user` in Local Dev

In local dev mode (`AUTH_BYPASS=true`), the Cognito deletion call will fail because `COGNITO_USER_POOL_ID` is an empty string. This is acceptable — tests should mock the Cognito client entirely. In production, the Cognito credentials come from the Lambda execution role.

For tests: mock `boto3.client` or mock `account_service.delete_account` at the service level.

### Frontend: signOut() Clears In-Memory Token

`signOut()` in `auth.js` clears the Cognito in-memory session. After calling it, the `getToken()` function returns null. `window.location.href = '/login'` then forces a full page reload to the login route. Do NOT use React Router `navigate()` here — a full page reload ensures all auth state is cleared.

### No Toast/Notification After Deletion

Since the user is redirected to login after account deletion, there is no point showing a success toast. The redirect itself is the confirmation. Only show inline error if the deletion fails.

### 200 vs 204 — Why 200

`apiFetch()` calls `response.json()` unconditionally after checking `response.ok`. A 204 No Content response has an empty body, causing `response.json()` to throw a SyntaxError. Return `{"deleted": True}` with status 200 to keep the frontend call simple. Other delete patterns in the codebase that use `apiFetch` follow the same approach.

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None.

### Completion Notes List

- Implemented `account_service.delete_account()` following the exact DynamoDB key structures specified: Sessions (PK=userId, SK=sk), QueryUsage (PK=userId, SK=date with reserved-word workaround), Feedback (scan with pagination since no GSI on userId). Cognito deleted last.
- Router returns `{"deleted": True}` with 200 (not 204) so `apiFetch` can call `response.json()` without error.
- Frontend Profile.jsx: added 3 state vars, `handleDeleteAccount`, and inline danger zone below "Your data" section. On success calls `signOut()` then hard-redirects to `/login`.
- 5 new backend tests all pass; 17 regression tests (sessions, feedback, export) all pass. Zero regressions.

### File List

- backend/services/account_service.py (NEW)
- backend/routers/account.py (NEW)
- backend/tests/test_account.py (NEW)
- backend/main.py (MODIFIED — added account_router import and include_router)
- frontend/src/api.js (MODIFIED — added deleteAccount())
- frontend/src/pages/Profile.jsx (MODIFIED — added danger zone UI, imports, state, handler)

## Change Log

- 2026-04-26: Story 5.3 created — Account Deletion. Adds DELETE /account endpoint, cascading DynamoDB + Cognito deletion, inline confirmation UI in Profile.
- 2026-04-26: Story 5.3 implemented — all tasks complete, 5 new tests pass, 0 regressions.
