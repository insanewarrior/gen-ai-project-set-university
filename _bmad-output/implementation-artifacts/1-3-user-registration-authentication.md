# Story 1.3: User Registration & Authentication

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **athlete**,
I want to create an account with my email and sign in/out securely,
So that my training data is private and I can access it across sessions.

## Acceptance Criteria

1. **Given** I am a new user on the sign-up page **When** I enter my email and password and submit **Then** a Cognito account is created, I receive a verification email, and after verification I am signed in and redirected to the Dashboard **And** the sport selector appears post-signup asking "What do you train?" with options: Grip Sport, Armwrestling, Powerlifting, General Strength

2. **Given** I am a registered user on the sign-in page **When** I enter my email and password **Then** I am authenticated via Cognito, a JWT token is stored in memory (not localStorage), and I am redirected to the Dashboard

3. **Given** I am signed in **When** I tap the sign-out action **Then** my JWT is cleared, I am redirected to the sign-in page, and subsequent API calls return 401

4. **Given** any API endpoint (other than health check) **When** a request is made without a valid Cognito JWT **Then** the request is rejected with a 401 status code (NFR7)

5. **Given** the local development environment is running **When** AUTH_BYPASS=true is set in .env **Then** the auth middleware injects TEST_USER_ID from .env, allowing development without a Cognito connection

## Tasks / Subtasks

- [x] Task 1: Add JWT verification dependencies to backend (AC: #4, #5)
  - [x] 1.1: Add `python-jose[cryptography]` to `backend/requirements.txt` for Cognito JWT verification
  - [x] 1.2: Add `httpx` to `backend/requirements.txt` for JWKS key fetching (already in test deps — move to prod or use `requests`)
  - [x] 1.3: Add `COGNITO_USER_POOL_ID` and `COGNITO_REGION` to `backend/config.py` (read from env, empty string default for local dev)
  - [x] 1.4: Update `.env.example` with `COGNITO_USER_POOL_ID` and `COGNITO_REGION` (commented out for local dev)

- [x] Task 2: Implement backend auth middleware (AC: #4, #5)
  - [x] 2.1: Create `backend/middleware/auth.py` — implement `get_current_user` as a FastAPI dependency
  - [x] 2.2: AUTH_BYPASS mode: if `config.AUTH_BYPASS == "true"`, skip JWT verification and return `config.TEST_USER_ID` as the user ID
  - [x] 2.3: Production mode: extract `Authorization: Bearer <token>` header; return 401 if missing
  - [x] 2.4: Fetch Cognito JWKS from `https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json` on first call; cache the keys in module-level dict (warm cache per Lambda instance)
  - [x] 2.5: Verify JWT signature using `python-jose`'s `jwt.decode()` with fetched public keys and `algorithms=["RS256"]`
  - [x] 2.6: Validate claims: `iss` matches Cognito pool URL, `aud`/`client_id` matches env var (optional strictness for MVP), `exp` not expired
  - [x] 2.7: Extract user ID from JWT `sub` claim; also extract `custom:sport` if present (for post-signup sport preference)
  - [x] 2.8: Return 401 with `{"error": "Unauthorized", "code": "INVALID_TOKEN"}` for any verification failure
  - [x] 2.9: Export `get_current_user` dependency and `CurrentUser` type alias (`str` = userId)

- [x] Task 3: Wire auth middleware into FastAPI app (AC: #4, #5)
  - [x] 3.1: In `backend/main.py`, update CORS `allow_origins` to include the CloudFront URL in addition to `http://localhost:5173` (use `*` for MVP or read from env)
  - [x] 3.2: Create a simple auth router test: `GET /me` endpoint that returns `{"userId": current_user}` using `Depends(get_current_user)` — useful for debugging and AC verification
  - [x] 3.3: All future routers will add `Depends(get_current_user)` to their path operations — document this pattern in the `/me` endpoint as the reference implementation

- [x] Task 4: Backend tests for auth middleware (AC: #4, #5)
  - [x] 4.1: In `backend/tests/test_auth.py`, test that `GET /health` returns 200 without auth header
  - [x] 4.2: Test that `GET /me` returns 401 when no Authorization header is provided (AUTH_BYPASS=false)
  - [x] 4.3: Test that `GET /me` returns 401 when Authorization header has invalid/malformed JWT (AUTH_BYPASS=false)
  - [x] 4.4: Test that `GET /me` returns 200 with userId when AUTH_BYPASS=true — no Cognito needed
  - [x] 4.5: Use `conftest.py` fixture for test client; set `AUTH_BYPASS=true` for integration tests that need a user context

- [x] Task 5: Install Cognito auth library in frontend (AC: #1, #2, #3)
  - [x] 5.1: `cd frontend && npm install amazon-cognito-identity-js` — lightweight official Cognito SDK (~45KB gzipped, no Amplify bloat)
  - [x] 5.2: Verify import works: `import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js'`

- [x] Task 6: Create frontend auth helper (AC: #1, #2, #3)
  - [x] 6.1: Create `frontend/src/auth.js` — Cognito auth helper
  - [x] 6.2: Implement `initUserPool()`: creates `CognitoUserPool` from `VITE_COGNITO_USER_POOL_ID` + `VITE_COGNITO_CLIENT_ID` env vars
  - [x] 6.3: Implement `signUp(email, password)`: calls `userPool.signUp()` — returns Promise resolving to `{ success, needsVerification, error }`
  - [x] 6.4: Implement `confirmSignUp(email, code)`: calls `CognitoUser.confirmRegistration()` — returns Promise resolving to `{ success, error }`
  - [x] 6.5: Implement `signIn(email, password)`: calls `AuthenticationDetails` + `CognitoUser.authenticateUser()` — on success, token is held by the SDK in memory (CognitoUserSession); returns `{ success, user, error }`
  - [x] 6.6: Implement `signOut()`: calls `cognitoUser.signOut()` — clears all session state
  - [x] 6.7: Implement `getToken()`: calls `cognitoUser.getSession()` and returns the `idToken.getJwtToken()` — returns null if no session. This is the JWT the backend expects.
  - [x] 6.8: Implement `getCurrentUser()`: calls `userPool.getCurrentUser()` — returns user if session exists (persists across page refresh via SDK's in-memory + cookie mechanism — `amazon-cognito-identity-js` uses localStorage by default; override with `Storage: sessionStorage` in `CognitoUserPoolData` to honor the "not localStorage" requirement, or use `ClientStorage` set to in-memory)
  - [x] 6.9: **CRITICAL — Token Storage**: Pass `Storage: { ... }` as in-memory store to `CognitoUserPool` constructor to ensure tokens are NOT persisted to localStorage. Example: implement a simple Map-based in-memory store conforming to the Storage interface. See architecture: "JWT token is stored in memory (not localStorage)"
  - [x] 6.10: Export: `{ signUp, confirmSignUp, signIn, signOut, getToken, getCurrentUser }`

- [x] Task 7: Update api.js to attach JWT tokens (AC: #2, #3)
  - [x] 7.1: Import `getToken` from `auth.js` in `api.js`
  - [x] 7.2: In `apiFetch()`, call `const token = await getToken()` before making the request
  - [x] 7.3: If `token` is not null, add `Authorization: Bearer ${token}` header to the request
  - [x] 7.4: Handle 401 responses from API: call `signOut()` and redirect to `/login` (use React Router navigation — pass a `navigate` function or use window.location for simplicity in MVP)
  - [x] 7.5: Update error handling: distinguish between 401 (auth error → redirect) and other errors (show inline error)

- [x] Task 8: Create auth pages (AC: #1, #2, #3)
  - [x] 8.1: Create `frontend/src/pages/SignIn.jsx` — email + password form, submit calls `signIn()`, redirects to `/` on success. Show inline error if sign-in fails (UX-DR19). Blue-500 primary "Sign In" button. Link to Sign Up page.
  - [x] 8.2: Create `frontend/src/pages/SignUp.jsx` — email + password form, submit calls `signUp()`. On success, show verification code input field (inline — no page navigation). Enter code → `confirmSignUp()` → redirect to post-signup sport selector. Ghost "Already have an account? Sign in" link.
  - [x] 8.3: Create `frontend/src/pages/SportSelect.jsx` — post-signup "What do you train?" screen. Four options: Grip Sport, Armwrestling, Powerlifting, General Strength. SportSelector component (from UX-DR10). After selection, store in component state or Cognito user attribute (call `updateUserAttributes` with `custom:sport`), redirect to Dashboard. This screen only appears once after signup.
  - [x] 8.4: All auth pages use the same dark theme (Zinc-900 background), system font, centered content card (max-width 400px, Zinc-800 card, 8px radius, 24px padding)
  - [x] 8.5: Form inputs follow the pattern from UX spec: Zinc-800 bg, Zinc-700 border, 6px radius, 16px font-size (prevents iOS zoom), focus Blue-400 ring

- [x] Task 9: Protect routes with auth state (AC: #1, #2, #3)
  - [x] 9.1: In `frontend/src/App.jsx`, add auth state: `const [user, setUser] = useState(null)` and `const [authLoading, setAuthLoading] = useState(true)`
  - [x] 9.2: On mount, call `getCurrentUser()` to check if existing session exists; set `user` state accordingly; set `authLoading = false` when done
  - [x] 9.3: While `authLoading` is true, show a minimal loading screen (Zinc-900 background, no skeleton — just blank dark screen to prevent flash of unauthenticated content)
  - [x] 9.4: If `user` is null, show auth routes only (`/login`, `/signup`). Redirect any other path to `/login`.
  - [x] 9.5: If `user` is not null, show main app routes (Dashboard `/`, Log `/log`, Chat `/chat`, History `/history`). Redirect `/login` and `/signup` to `/`.
  - [x] 9.6: Pass a `signOut` handler through context or props that calls `auth.signOut()` and resets `user` state to null

- [x] Task 10: Add sign-out action to UI (AC: #3)
  - [x] 10.1: Add a sign-out button in the app. Based on the UX spec, a Ghost button in the Header or a settings area is appropriate. For MVP, add "Sign Out" as a Ghost button in `HeaderBar.jsx` (visible when on Desktop sidebar) or accessible from the Dashboard
  - [x] 10.2: On tap, call `signOut()` from auth.js, reset `user` state in App.jsx, navigate to `/login`
  - [x] 10.3: Test: after sign-out, verify that the next API call from the browser returns 401 (no token attached to `api.js` requests)

- [x] Task 11: Configure frontend environment variables (AC: #1, #2)
  - [x] 11.1: Create `frontend/.env.example` with `VITE_COGNITO_USER_POOL_ID=` and `VITE_COGNITO_CLIENT_ID=` (empty — must be filled from CDK outputs after deploy)
  - [x] 11.2: Add `VITE_API_URL=http://localhost:8080` to `frontend/.env.example` for local dev
  - [x] 11.3: Document in auth.js: "Get UserPoolId and ClientId from CDK outputs file at `infra/cdk-outputs.json` after running `make deploy`"
  - [x] 11.4: Create `frontend/.env.local` (gitignored) instructions in `.env.example` comments — developers copy to `.env.local` and fill in their values

- [x] Task 12: Update CDK stack to expose Cognito custom attribute (AC: #1)
  - [x] 12.1: In `infra/stacks/strengthwise_stack.py`, add `custom_attributes` to the Cognito user pool: `{"sport": cognito.StringAttribute(mutable=True)}` — needed for sport selection post-signup storage
  - [x] 12.2: Verify existing `UserPoolId` and `UserPoolClientId` CfnOutputs are still present (they were added in Story 1.2 — do NOT remove them)

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow these patterns exactly:**

- **JWT in memory only:** `amazon-cognito-identity-js` defaults to localStorage. Override `Storage` in `CognitoUserPoolData` with an in-memory Map implementation. This is non-negotiable per NFR and architecture spec. Do NOT leave the default.
- **Auth middleware is FastAPI dependency injection, NOT HTTP middleware:** Use `Depends(get_current_user)` per route, not `app.add_middleware()`. This gives per-route control and is easier to test.
- **The /health endpoint MUST remain unauthenticated** — it has no `Depends(get_current_user)`. All other endpoints added in future stories will include the dependency.
- **No Cognito authorizer on API Gateway** — auth is handled entirely in FastAPI middleware, not at the API Gateway layer. This matches the architecture decision from Story 1.2: "Do NOT add Cognito authorizer to API Gateway in this story."
- **AUTH_BYPASS=true in local dev** — all backend integration tests use this mode. Do not write tests that depend on real Cognito JWTs.
- **Routers are thin** — the `GET /me` debug endpoint returns just `{"userId": current_user}`. No business logic. Business logic lives in services/.
- **camelCase JSON responses** — `{"userId": "..."}` not `{"user_id": "..."}` (per architecture naming convention).

### Backend JWT Verification Pattern

```python
# backend/middleware/auth.py

import os
from functools import lru_cache
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

import config

security = HTTPBearer(auto_error=False)

_jwks_cache: Optional[dict] = None  # module-level cache per Lambda instance

def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        region = config.COGNITO_REGION
        pool_id = config.COGNITO_USER_POOL_ID
        url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    # AUTH_BYPASS mode for local development
    if config.AUTH_BYPASS.lower() == "true":
        return config.TEST_USER_ID

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "code": "MISSING_TOKEN"},
        )

    token = credentials.credentials
    try:
        jwks = _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Cognito uses client_id in aud, skip strict check
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail={"error": "Unauthorized", "code": "INVALID_TOKEN"})
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error": "Token expired", "code": "TOKEN_EXPIRED"})
    except JWTError:
        raise HTTPException(status_code=401, detail={"error": "Unauthorized", "code": "INVALID_TOKEN"})

# Type alias for cleaner router signatures
CurrentUser = str
```

**Note on `verify_aud=False`:** Cognito access tokens use `client_id` in the `aud` claim, not the pool ID. Setting `verify_aud=False` avoids a verification error — the `iss` claim (Cognito pool URL) is still verified by default and is sufficient for security at this scale.

### Frontend In-Memory Token Storage

```javascript
// frontend/src/auth.js (key pattern)

// In-memory storage that satisfies the Storage interface
const memoryStore = new Map();
const inMemoryStorage = {
  setItem: (key, value) => memoryStore.set(key, value),
  getItem: (key) => memoryStore.get(key) ?? null,
  removeItem: (key) => memoryStore.delete(key),
  clear: () => memoryStore.clear(),
};

const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
  Storage: inMemoryStorage,  // REQUIRED: prevents localStorage persistence
};

const userPool = new CognitoUserPool(poolData);
```

**Consequence of in-memory storage:** Sessions do NOT persist across page refreshes. On refresh, the user must sign in again. This is acceptable for MVP — it is a known trade-off for storing JWT in memory vs. localStorage. The UX should handle this gracefully (redirect to sign-in, not a crash).

### Frontend Auth State Flow

```
App.jsx mounts
  → getCurrentUser() → null (no in-memory session after refresh)
  → user = null, authLoading = false
  → show SignIn.jsx at /login

User signs in successfully
  → auth.js signIn() → CognitoUserSession stored in memoryStore
  → setUser(cognitoUser)
  → React Router navigates to /

User submits API request
  → api.js → getToken() → idToken.getJwtToken()
  → adds Authorization: Bearer <jwt>
  → backend verifies, returns data

User signs out
  → auth.js signOut() → memoryStore.clear()
  → setUser(null)
  → navigate to /login
```

### Config Changes Needed

Add to `backend/config.py`:
```python
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
```

Add to `.env.example`:
```
# Cognito configuration — fill from CDK outputs after deploy
# COGNITO_USER_POOL_ID=us-east-1_xxxxx
# COGNITO_REGION=us-east-1
```

### Post-Signup Sport Selection

The sport selector on the SignUp flow (AC #1) uses the `SportSelector` component from UX-DR10. For storage of the selected sport:
- **Option A (MVP):** Store in Cognito `custom:sport` user attribute via `cognitoUser.updateAttributes([{ Name: 'custom:sport', Value: selectedSport }])` — persists server-side, recoverable
- **Option B (simpler MVP):** Store in component state and pass to Dashboard — does not persist but acceptable if sign-in always starts fresh (since memory storage)

Recommendation: **Option A** — it's a single additional API call and avoids re-asking on every sign-in. The CDK stack must add `custom:sport` as a mutable custom attribute.

### Cognito Custom Attribute in CDK

```python
# infra/stacks/strengthwise_stack.py — update Cognito user pool
user_pool = cognito.UserPool(self, "UserPool",
    self_sign_up_enabled=True,
    sign_in_aliases=cognito.SignInAliases(email=True),
    auto_verify=cognito.AutoVerifiedAttrs(email=True),
    custom_attributes={
        "sport": cognito.StringAttribute(mutable=True),
    },
    removal_policy=RemovalPolicy.DESTROY,
)
```

**IMPORTANT:** Cognito custom attributes are prefixed with `custom:` when read from JWT claims. The attribute is stored as `custom:sport` but accessed in the JWT payload as `custom:sport`.

### New Endpoint: GET /me

```python
# backend/main.py (or a new router/profile.py)
from middleware.auth import get_current_user

@app.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"userId": current_user}
```

This serves as:
1. The reference implementation for how to protect endpoints
2. A way to verify auth is working in local dev and post-deploy testing
3. AC #4 verification: call `/me` without token → expect 401

### File Structure

Files this story creates or modifies:

```
backend/
├── middleware/
│   └── auth.py                   # NEW — JWT verification + AUTH_BYPASS mode
├── config.py                     # MODIFY — add COGNITO_USER_POOL_ID, COGNITO_REGION
├── main.py                       # MODIFY — add GET /me endpoint with auth dependency
├── requirements.txt              # MODIFY — add python-jose[cryptography], requests or httpx
├── tests/
│   └── test_auth.py              # NEW — auth middleware tests
└── .env / .env.example           # MODIFY — add COGNITO_USER_POOL_ID, COGNITO_REGION

frontend/
├── src/
│   ├── auth.js                   # NEW — Cognito auth helper with in-memory storage
│   ├── api.js                    # MODIFY — attach JWT token to requests, handle 401
│   ├── App.jsx                   # MODIFY — auth state, protected routes
│   ├── pages/
│   │   ├── SignIn.jsx             # NEW — sign-in form
│   │   ├── SignUp.jsx             # NEW — sign-up + verification code form
│   │   └── SportSelect.jsx       # NEW — post-signup sport selection
├── .env.example                  # NEW — VITE_COGNITO_USER_POOL_ID, VITE_COGNITO_CLIENT_ID
└── package.json                  # MODIFY — add amazon-cognito-identity-js

infra/
└── stacks/
    └── strengthwise_stack.py     # MODIFY — add custom:sport attribute to Cognito user pool
```

### Testing Requirements

**Backend (pytest):**
- Test `GET /health` → 200 without Authorization header
- Test `GET /me` with `AUTH_BYPASS=false` and no token → 401 with `{"code": "MISSING_TOKEN"}`
- Test `GET /me` with `AUTH_BYPASS=false` and invalid token → 401 with `{"code": "INVALID_TOKEN"}`
- Test `GET /me` with `AUTH_BYPASS=true` → 200 with `{"userId": "test-user-001"}`
- Use `backend/tests/conftest.py` to set `AUTH_BYPASS=true` for tests that need an authenticated user

**Frontend (manual — no Vitest tests required for auth in MVP):**
- Manual test: sign-up flow end-to-end (signup → verify email → sport select → dashboard)
- Manual test: sign-in with valid credentials → dashboard
- Manual test: sign-out → redirect to login
- Manual test: page refresh after sign-in → redirect to login (expected behavior with in-memory storage)
- Manual test: navigate to `/` without auth → redirect to `/login`

### UX Design Compliance

Per UX spec and UX-DR patterns:

- **Auth pages visual style:** Zinc-900 bg, centered Zinc-800 card (400px max-width, 8px radius), system font, 16px body text
- **Form inputs:** Zinc-800 bg, Zinc-700 border, 6px radius, Blue-400 focus ring, Red-500 error state (inline, not modal)
- **Primary button:** Blue-500 bg ("Sign In", "Create Account"), minimum 44px height, full-width on mobile
- **Ghost link:** "Already have an account? Sign in" in Zinc-400 text (UX-DR18)
- **No onboarding questionnaires** — only one post-signup question: "What do you train?" (UX spec explicitly forbids onboarding questionnaires beyond sport selection)
- **No modal dialogs** — email verification code input appears inline in the sign-up form (UX-DR19)
- **Inline error feedback** — wrong password, unverified account, network errors all show below the form in Red-400 text (not modal)

### Previous Story Intelligence

**From Story 1.2:**
- Cognito user pool is **already provisioned** in AWS. Do NOT create a new one.
- CDK outputs include `UserPoolId` and `UserPoolClientId` — these are the values needed for `VITE_COGNITO_USER_POOL_ID` and `VITE_COGNITO_CLIENT_ID` in the frontend env
- CDK outputs file lives at `infra/cdk-outputs.json` after running `make deploy`
- The Cognito user pool was created with `self_sign_up_enabled=True` and `sign_in_aliases=cognito.SignInAliases(email=True)` — confirmed in Story 1.2 completion notes
- The Cognito user pool has `auth_flows=AuthFlow(user_srp=True)` on the client — the `amazon-cognito-identity-js` SDK uses SRP auth by default, which matches this config
- API Gateway CORS is configured with `allow_origins=["*"]` — frontend auth flows (sign-up, sign-in) don't call API Gateway directly (they call Cognito's SDK), so CORS on API Gateway does not affect auth
- `backend/middleware/__init__.py` exists but is empty — add `auth.py` to the same directory
- `backend/main.py` currently only has the `/health` endpoint + CORS middleware — add `GET /me` endpoint here
- `backend/config.py` has `AUTH_BYPASS`, `TEST_USER_ID` already — these are the exact vars used by the auth middleware bypass mode

**From Story 1.1:**
- Separate Python venvs for `backend/` and `infra/` — install `python-jose[cryptography]` in the `backend/` venv, not the infra venv
- The existing `conftest.py` in `backend/tests/` uses `TestClient` from FastAPI — auth tests follow the same pattern

### Anti-Patterns to Avoid

- **DO NOT** use the full AWS Amplify library (`aws-amplify`) — it's 500KB+ and includes much more than auth. Use `amazon-cognito-identity-js` only.
- **DO NOT** store JWT in localStorage — use in-memory Map as described above. Storing in localStorage is a security risk and explicitly violates the architecture spec.
- **DO NOT** configure Cognito Authorizer on API Gateway — auth is in FastAPI middleware only. Adding it at API Gateway would create two auth layers and complicate the architecture.
- **DO NOT** put auth logic in routers — auth is a dependency (`Depends(get_current_user)`), not inline code in each route handler.
- **DO NOT** create separate user records in DynamoDB for this story — Cognito `sub` (UUID) is the user ID used directly in all DynamoDB operations. No separate users table.
- **DO NOT** use `os.environ.get` directly in middleware — always use `config.py` constants for consistency.
- **DO NOT** catch `Exception` broadly in auth middleware — only catch `JWTError` and `ExpiredSignatureError` specifically.
- **DO NOT** hardcode the Cognito region — read from `config.COGNITO_REGION`.

### Project Structure Notes

The existing `frontend/src/App.jsx` likely renders all 4 screens directly. It needs to be refactored to add an auth gate:

```jsx
// App.jsx pattern
function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setAuthLoading(false);
  }, []);

  if (authLoading) return <div className="min-h-screen bg-zinc-900" />;

  return (
    <Router>
      {user ? (
        <AuthenticatedApp user={user} onSignOut={() => { signOut(); setUser(null); }} />
      ) : (
        <Routes>
          <Route path="/signup" element={<SignUp onSuccess={() => setUser(getCurrentUser())} />} />
          <Route path="*" element={<SignIn onSuccess={() => setUser(getCurrentUser())} />} />
        </Routes>
      )}
    </Router>
  );
}
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security] — Cognito JWT, auth flow, AUTH_BYPASS pattern, no localStorage
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns] — 401 response format, error JSON structure
- [Source: _bmad-output/planning-artifacts/architecture.md#Process Patterns] — Auth pattern: memory storage, middleware injection
- [Source: _bmad-output/planning-artifacts/architecture.md#Enforcement Guidelines] — All AI Agents MUST follow camelCase JSON, use Depends() pattern
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries] — middleware/auth.py location, auth.js location
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3] — Acceptance criteria, FR19, FR20, NFR7
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation] — Zinc-800 card, form input styling, button hierarchy
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#UX Consistency Patterns] — Inline error patterns, no modal dialogs, button tiers
- [Source: _bmad-output/implementation-artifacts/1-2-aws-infrastructure-deployment-pipeline.md] — Cognito user pool already provisioned, CDK outputs for UserPoolId/ClientId, CORS config

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- test_me_returns_401_with_invalid_token initially failed because module reload reset `_jwks_cache` to None before the mock could take effect. Fixed by patching `_get_jwks` directly via `monkeypatch.setattr` after reload instead of patching the cache value.

### Completion Notes List

- **Task 1–4 (Backend):** Added `python-jose[cryptography]` and `httpx` to requirements.txt. Added `COGNITO_USER_POOL_ID` and `COGNITO_REGION` to config.py. Created `backend/middleware/auth.py` with `get_current_user` FastAPI dependency supporting AUTH_BYPASS mode and production JWT verification via Cognito JWKS (module-level cached). Updated `main.py` to add `GET /me` as reference auth-protected endpoint and support CLOUDFRONT_URL in CORS origins. 8/8 backend tests pass including /health public access, 401 on missing/invalid token, 200 with AUTH_BYPASS=true.
- **Task 5–7 (Frontend core):** Installed `amazon-cognito-identity-js`. Created `auth.js` with Map-based in-memory storage (no localStorage) overriding CognitoUserPool default. Implements signUp, confirmSignUp, signIn, signOut, getToken, getCurrentUser, updateSport. Updated `api.js` to call `getToken()` and attach `Authorization: Bearer` header; 401 responses trigger signOut + redirect to /login.
- **Task 8 (Auth pages):** Created SignIn.jsx (email/password, inline error, link to signup), SignUp.jsx (signup + inline verification code entry, no page change), SportSelect.jsx (4 sport options, saves custom:sport via Cognito updateAttributes, redirects to dashboard). All pages follow dark theme spec (Zinc-900 bg, Zinc-800 card, 400px max-width, 8px radius, 16px inputs, Blue-500 CTA, Red-400 inline errors).
- **Task 9–10 (Auth routing & sign-out):** Restructured App.jsx as auth-aware root with authLoading blank screen, user state from getCurrentUser(). Unauthenticated routes: /signup, /sport-select, /* → SignIn. Authenticated routes: nested under AuthenticatedShell with redirect for /login and /signup. Simplified main.jsx to BrowserRouter + App only. HeaderBar updated to accept optional onSignOut prop and renders a ghost sign-out button when provided.
- **Task 11 (Frontend env):** Created frontend/.env.example with VITE_COGNITO_USER_POOL_ID, VITE_COGNITO_CLIENT_ID, VITE_API_URL (localhost:8080 for local dev).
- **Task 12 (CDK):** Added `custom_attributes={"sport": cognito.StringAttribute(mutable=True)}` to the Cognito UserPool in strengthwise_stack.py. UserPoolId and UserPoolClientId CfnOutputs confirmed present.
- Frontend builds successfully (vite build: 0 errors, 77 modules transformed).

### File List

- `backend/requirements.txt` — added `python-jose[cryptography]`, `httpx`
- `backend/config.py` — added `COGNITO_USER_POOL_ID`, `COGNITO_REGION`
- `backend/.env.example` — new file with Cognito config comments
- `backend/middleware/auth.py` — new file: `get_current_user` FastAPI dependency, JWKS cache, AUTH_BYPASS mode
- `backend/main.py` — added `GET /me` endpoint, updated CORS to support CLOUDFRONT_URL env var
- `backend/tests/test_auth.py` — new file: 5 auth middleware tests
- `frontend/package.json` — added `amazon-cognito-identity-js`
- `frontend/package-lock.json` — updated lockfile
- `frontend/src/auth.js` — new file: Cognito auth helper with in-memory token storage
- `frontend/src/api.js` — updated: JWT token attachment, 401 handling with signOut + redirect
- `frontend/src/App.jsx` — rewritten: auth-aware root with user state, auth loading screen, protected/public route split
- `frontend/src/main.jsx` — simplified: BrowserRouter + App only (route definitions moved to App.jsx)
- `frontend/src/pages/SignIn.jsx` — new file: sign-in form
- `frontend/src/pages/SignUp.jsx` — new file: sign-up + inline email verification
- `frontend/src/pages/SportSelect.jsx` — new file: post-signup sport selection
- `frontend/src/components/HeaderBar.jsx` — updated: optional onSignOut prop and ghost sign-out button
- `frontend/.env.example` — new file: VITE_COGNITO_USER_POOL_ID, VITE_COGNITO_CLIENT_ID, VITE_API_URL
- `infra/stacks/strengthwise_stack.py` — added `custom:sport` Cognito custom attribute, reformatted HttpLambdaIntegration line

## Change Log

- 2026-04-25: Implemented Story 1.3 — User Registration & Authentication. Added backend JWT middleware with AUTH_BYPASS support, 5 backend tests (8 total pass), frontend Cognito auth helper with in-memory token storage, SignIn/SignUp/SportSelect pages, auth-gated routing in App.jsx, sign-out in HeaderBar, frontend .env.example, and custom:sport Cognito attribute in CDK stack.
