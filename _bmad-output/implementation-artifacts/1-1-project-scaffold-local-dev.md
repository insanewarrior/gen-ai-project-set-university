# Story 1.1: Project Scaffold & Local Development Environment

Status: review

## Story

As a **developer**,
I want a complete project scaffold with backend, frontend, and IaC directories and a working local dev environment,
So that I have a solid foundation to build all features on.

## Acceptance Criteria

1. **Given** a fresh checkout of the repository **When** I run `make dev` (or `scripts/dev.sh`) **Then** DynamoDB Local starts on port 8000, FastAPI backend starts on port 8080 with a `/health` endpoint returning 200, and Vite dev server starts on port 5173 serving the React app **And** the directory structure matches the architecture specification (backend/, frontend/, infra/, scripts/, Makefile)

2. **Given** the FastAPI backend is running locally **When** I call `GET /health` **Then** I receive a 200 response confirming the API is operational **And** the Mangum adapter is configured so the same handler works on Lambda

3. **Given** the frontend scaffold is initialized **When** I open the Vite dev server in a browser **Then** I see a basic React app with Tailwind CSS v4 configured, dark theme (Zinc-900 background), system font stack, and the 4-tab navigation shell (Home, Log, Chat, History)

4. **Given** the infra/ directory is initialized **When** I inspect the CDK project **Then** it contains a Python CDK app with a single stack shell ready for resource definitions

## Tasks / Subtasks

- [x] Task 1: Initialize project root structure (AC: #1)
  - [x] 1.1: Create directory tree: `backend/`, `frontend/`, `infra/`, `scripts/`
  - [x] 1.2: Create root `Makefile` with targets: `dev-backend`, `dev-frontend`, `dev` (runs all), `deploy`, `seed`
  - [x] 1.3: Create `.gitignore` (Python venvs, node_modules, .env, __pycache__, dist/, cdk.out/)
  - [x] 1.4: Create `.env.example` with all env vars documented (DYNAMODB_ENDPOINT, AUTH_BYPASS, CLAUDE_MODEL, TEST_USER_ID, FAISS_INDEX_PATH)
  - [x] 1.5: Create `README.md` with local dev setup instructions
- [x] Task 2: Initialize FastAPI backend (AC: #1, #2)
  - [x] 2.1: Create `backend/requirements.txt` — fastapi, mangum==0.21.0, uvicorn, boto3, pydantic
  - [x] 2.2: Create `backend/requirements-dev.txt` — pytest, httpx
  - [x] 2.3: Create `backend/main.py` — FastAPI app with `/health` endpoint + Mangum handler
  - [x] 2.4: Create `backend/config.py` — environment config via `os.environ` with defaults
  - [x] 2.5: Create empty module directories: `routers/`, `services/`, `models/`, `middleware/`, `data/`, `tests/` (each with `__init__.py`)
  - [x] 2.6: Create `backend/.env` from `.env.example` with local dev values
  - [x] 2.7: Verify `uvicorn main:app --reload --port 8080` starts and `/health` returns 200
- [x] Task 3: Initialize Vite + React frontend (AC: #3)
  - [x] 3.1: Run `npm create vite@latest frontend -- --template react` to scaffold
  - [x] 3.2: Install dependencies: `tailwindcss`, `@tailwindcss/vite`, `react-router-dom`
  - [x] 3.3: Configure `vite.config.js` with Tailwind plugin and API proxy to port 8080
  - [x] 3.4: Set up `src/index.css` with `@import "tailwindcss"` and custom design tokens
  - [x] 3.5: Create `src/App.jsx` — root layout with TabBar/Sidebar responsive navigation shell
  - [x] 3.6: Create `src/main.jsx` — React entry point with router setup (4 routes: `/`, `/log`, `/chat`, `/history`)
  - [x] 3.7: Create placeholder page components: `Dashboard.jsx`, `LogSession.jsx`, `Chat.jsx`, `History.jsx`
  - [x] 3.8: Create `src/components/TabBar.jsx` — bottom tab bar (mobile) / sidebar (desktop)
  - [x] 3.9: Create `src/components/HeaderBar.jsx` — 48px header with screen title
  - [x] 3.10: Create `src/api.js` — fetch wrapper stub (base URL switching, auth header placeholder)
  - [x] 3.11: Verify dark theme renders (Zinc-900 bg), navigation shell works, all 4 tabs route correctly
- [x] Task 4: Initialize AWS CDK infrastructure (AC: #4)
  - [x] 4.1: Run `cdk init app --language python` in `infra/`
  - [x] 4.2: Create `infra/stacks/strengthwise_stack.py` — empty single stack shell with TODO comments for resources
  - [x] 4.3: Update `infra/app.py` to instantiate the stack
  - [x] 4.4: Verify `cdk synth` succeeds (produces valid CloudFormation template)
- [x] Task 5: Create local dev startup scripts (AC: #1)
  - [x] 5.1: Create `scripts/dev.sh` — starts DynamoDB Local (Docker), backend (uvicorn), frontend (vite dev)
  - [x] 5.2: Wire Makefile `dev` target to `scripts/dev.sh`
  - [x] 5.3: Verify `make dev` launches all three services
- [x] Task 6: Validate full local dev loop
  - [x] 6.1: `make dev` starts all services without errors
  - [x] 6.2: `GET http://localhost:8080/health` returns 200
  - [x] 6.3: `http://localhost:5173` renders React app with dark theme and 4-tab nav
  - [x] 6.4: DynamoDB Local running on port 8000

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow the architecture document exactly. Do not deviate from these patterns:**

- **Backend framework:** FastAPI with Mangum v0.21.0 dual-mode adapter. Same handler code runs locally (uvicorn) and on Lambda. Entry point pattern:
  ```python
  from fastapi import FastAPI
  from mangum import Mangum
  
  app = FastAPI()
  handler = Mangum(app)  # Lambda entry point
  ```
- **Frontend framework:** Vite 8 + React (not Preact, not vanilla JS). Use `npm create vite@latest` with `--template react`
- **Styling:** Tailwind CSS v4 with first-party `@tailwindcss/vite` plugin. No separate `tailwind.config.js` needed in v4 — configure via CSS `@theme` directive in `index.css`
- **IaC:** AWS CDK v2 in Python. Single stack. `cdk init app --language python`
- **Testing:** pytest for backend (with httpx TestClient), Vitest for frontend (native to Vite)
- **Python venvs:** Separate venvs for `backend/` and `infra/` — they have different dependency trees. Do NOT share a single venv

### Config Pattern

Use `backend/config.py` reading from `os.environ` with defaults — no code branches for local vs. AWS:

```python
import os

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # None for AWS, "http://localhost:8000" for local
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
AUTH_BYPASS = os.getenv("AUTH_BYPASS", "false")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250514")
TEST_USER_ID = os.getenv("TEST_USER_ID", "test-user-001")
```

### Frontend Design Tokens (from UX Spec)

Apply these in `src/index.css` using Tailwind v4's `@theme` directive:

- **Background:** Zinc-900 (`#18181b`) — dark-first default
- **Surfaces:** Zinc-800 (`#27272a`) — cards, panels, form inputs
- **Accent personal:** Blue-400 (`#60a5fa`) — personal data citations
- **Accent knowledge:** Amber-400 (`#fbbf24`) — knowledge citations
- **Accent action:** Blue-500 (`#3b82f6`) — primary buttons, active tab
- **Success:** Green-500 (`#22c55e`)
- **Error:** Red-500 (`#ef4444`)
- **Font stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`
- **Body text:** 16px minimum (prevents iOS zoom on input focus)
- **Tab bar height:** 56px (mobile), hidden on md:+ (replaced by 200px sidebar)
- **Header bar:** 48px height
- **Touch targets:** 44x44px minimum

### Navigation Shell (from UX Spec)

Build the 4-tab navigation with responsive layout:

**Mobile (<768px):**
```
+----------------------+
| Header (48px)        |
+----------------------+
|                      |
|   Content area       |
|   (scrollable)       |
|                      |
+----------------------+
| Tab bar (56px)       |  ← Home | Log | Chat | History
+----------------------+
```

**Desktop (md: >=768px):**
```
+-------------------------------------+
| Header                              |
+----------+--------------------------+
| Sidebar  |                          |
| Nav      |   Content area           |
| (200px)  |   (max-width: 720px)     |
+----------+--------------------------+
```

- Active tab: Blue-500 icon + text
- Inactive tabs: Zinc-500 icon + text
- Tab transitions: instant (no animation)
- Routes: `/` (Dashboard), `/log` (LogSession), `/chat` (Chat), `/history` (History)

### Placeholder Pages

Each page should render a minimal placeholder that identifies the screen. These will be replaced in later stories:

- **Dashboard.jsx** — "StrengthWise" heading + placeholder text
- **LogSession.jsx** — "Log Session" heading + placeholder text
- **Chat.jsx** — "Chat" heading + placeholder text
- **History.jsx** — "History" heading + placeholder text

### DynamoDB Local

Use the official Docker image. The `scripts/dev.sh` should start it if not already running:
```bash
docker run -d --name dynamodb-local -p 8000:8000 amazon/dynamodb-local
```

### Makefile Targets

```makefile
dev-backend:    # cd backend && uvicorn main:app --reload --port 8080
dev-frontend:   # cd frontend && npm run dev
dev:            # scripts/dev.sh (starts DynamoDB Local + backend + frontend)
deploy:         # scripts/deploy.sh (placeholder for Story 1.2)
seed:           # scripts/seed.sh (placeholder for later)
```

### Anti-Patterns to Avoid

- Do NOT put business logic in routers — routers are thin (validate input, call service, return response)
- Do NOT hardcode DynamoDB table names — use `config.py`
- Do NOT add state management libraries (no Redux, no Zustand) — `useState` + `fetch` is sufficient
- Do NOT add custom fonts — use system font stack for instant loading
- Do NOT create a shared Python venv — backend/ and infra/ have separate dependency trees
- Do NOT use `type="number"` for numeric inputs — use `inputmode="decimal"` or `inputmode="numeric"` instead
- Do NOT add `tailwind.config.js` — Tailwind v4 uses CSS-based configuration via `@theme`

### CORS Setup

Configure FastAPI CORSMiddleware to allow the Vite dev server origin:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Project Structure Notes

The complete directory tree this story must produce (empty directories with `__init__.py` where applicable):

```
strengthwise/              # or project root
├── README.md
├── Makefile
├── .gitignore
├── .env.example
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env
│   ├── routers/__init__.py
│   ├── services/__init__.py
│   ├── models/__init__.py
│   ├── middleware/__init__.py
│   ├── data/
│   └── tests/
│       ├── __init__.py
│       └── conftest.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api.js
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── LogSession.jsx
│       │   ├── Chat.jsx
│       │   └── History.jsx
│       └── components/
│           ├── TabBar.jsx
│           └── HeaderBar.jsx
├── infra/
│   ├── app.py
│   ├── cdk.json
│   ├── requirements.txt
│   └── stacks/
│       └── strengthwise_stack.py
└── scripts/
    ├── dev.sh
    ├── deploy.sh
    ├── teardown.sh
    └── seed.sh
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Starter Template Evaluation] — Vite 8 + React selection, CDK init commands
- [Source: _bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions] — FastAPI + Mangum pattern, config.py, DynamoDB table design
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries] — Complete directory tree, naming conventions
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules] — Naming patterns, anti-patterns, enforcement guidelines
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation] — Tailwind v4, color system, typography, spacing
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#UX Consistency Patterns] — Navigation patterns, responsive layout, tab bar spec
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1] — Acceptance criteria, user story

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- Backend pytest: 1 test passed (test_health_returns_200)
- Frontend vite build: successful, 30 modules transformed
- CDK synth: successful, valid CloudFormation template produced
- Mangum handler verified via Python import

### Completion Notes List

- Created complete project scaffold matching architecture spec
- FastAPI backend with /health endpoint + Mangum dual-mode adapter (local uvicorn + Lambda)
- CORS configured for Vite dev server origin
- Config pattern via os.environ with defaults in backend/config.py
- Vite 8 + React frontend with Tailwind CSS v4 (@tailwindcss/vite plugin, CSS-based @theme config)
- Dark theme (Zinc-900 bg) with full design token system from UX spec
- Responsive 4-tab navigation shell: bottom TabBar (mobile) / sidebar (desktop)
- Router with 4 routes: /, /log, /chat, /history with placeholder page components
- API fetch wrapper stub with base URL switching
- AWS CDK v2 Python stack shell with TODO placeholders for Story 1.2 resources
- Separate Python venvs for backend/ and infra/ (different dependency trees)
- dev.sh script starts DynamoDB Local (Docker), backend, and frontend with cleanup trap
- Makefile with dev, dev-backend, dev-frontend, deploy, seed targets

### File List

- Makefile (new)
- .gitignore (modified)
- .env.example (new)
- README.md (new)
- backend/main.py (new)
- backend/config.py (new)
- backend/requirements.txt (new)
- backend/requirements-dev.txt (new)
- backend/.env (new)
- backend/routers/__init__.py (new)
- backend/services/__init__.py (new)
- backend/models/__init__.py (new)
- backend/middleware/__init__.py (new)
- backend/tests/__init__.py (new)
- backend/tests/conftest.py (new)
- backend/tests/test_health.py (new)
- frontend/vite.config.js (modified)
- frontend/src/index.css (modified)
- frontend/src/main.jsx (modified)
- frontend/src/App.jsx (modified)
- frontend/src/api.js (new)
- frontend/src/pages/Dashboard.jsx (new)
- frontend/src/pages/LogSession.jsx (new)
- frontend/src/pages/Chat.jsx (new)
- frontend/src/pages/History.jsx (new)
- frontend/src/components/TabBar.jsx (new)
- frontend/src/components/HeaderBar.jsx (new)
- infra/app.py (new)
- infra/cdk.json (new)
- infra/requirements.txt (new)
- infra/stacks/__init__.py (new)
- infra/stacks/strengthwise_stack.py (new)
- scripts/dev.sh (new)
- scripts/deploy.sh (new)
- scripts/seed.sh (new)
- scripts/teardown.sh (new)

## Change Log

- 2026-04-24: Story 1.1 implemented — full project scaffold with backend (FastAPI+Mangum), frontend (Vite+React+Tailwind v4), infra (CDK Python), and local dev scripts
