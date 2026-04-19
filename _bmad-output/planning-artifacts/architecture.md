---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: complete
completedAt: '2026-04-20'
lastStep: 8
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/product-brief-strengthwise.md'
  - '_bmad-output/planning-artifacts/product-brief-strengthwise-distillate.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
  - '_bmad-output/planning-artifacts/research/market-strengthwise-ai-coaching-research-2026-04-18.md'
workflowType: 'architecture'
project_name: 'StrengthWise'
user_name: 'Mr.A'
date: '2026-04-20'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (33 total):**

| Category | FRs | Architectural Impact |
|----------|-----|---------------------|
| Training Session Logging (FR1-FR7) | Structured CRUD with sport-specific exercise database | DynamoDB schema design, Lambda handlers, exercise taxonomy data model |
| AI Coaching / Dual-Source RAG (FR8-FR14) | Personal history retrieval + general knowledge retrieval + LLM synthesis with dual citations | FAISS index on S3/Lambda, DynamoDB query patterns for user training data, prompt engineering for citation formatting, confidence calibration |
| Rate Limiting & Usage Tiers (FR15-FR18) | Per-user daily query caps with tiered access (free/onboarding/premium) | API Gateway usage plans or DynamoDB counter-based tracking, tier logic in Lambda |
| User Account Management (FR19-FR23) | Auth, export, deletion | Cognito user pools, CSV generation Lambda, cascading data deletion |
| Knowledge Base & Exercises (FR24-FR26) | Curated corpus + sport-specific exercise DB + cross-domain transfer | FAISS embedding pipeline, exercise reference data (DynamoDB or static config), prompt design for cross-domain bridging |
| Safety & Infrastructure (FR27-FR33) | Disclaimers, feedback, input validation, IaC, monitoring, index rebuild | Input sanitization middleware, DynamoDB feedback table, CDK/Terraform stack, CloudWatch dashboards |

**Non-Functional Requirements (27 total):**

| Category | Key NFRs | Architectural Driver |
|----------|----------|---------------------|
| Performance | NFR1: <500ms logging, NFR2: <10s AI query, NFR5: <3s TTI on 4G | Lambda cold start optimization, FAISS index size management, CloudFront caching, minimal frontend bundle |
| Security | NFR7-NFR13: Cognito JWT on all endpoints, encryption at rest, input sanitization, rate limit enforcement server-side | API Gateway authorizer, DynamoDB default encryption, Lambda input validation layer |
| Scalability | NFR14-NFR17: 100 concurrent users, bounded LLM costs, FAISS in Lambda memory, efficient DynamoDB queries | Lambda auto-scaling, on-demand DynamoDB capacity, FAISS file <512MB, GSI design for user+date queries |
| Accessibility | NFR18-NFR21: WCAG 2.1 AA, keyboard nav, 44px touch targets | Frontend implementation concern — semantic HTML, ARIA, Tailwind responsive utilities |
| Integration | NFR22-NFR24: Graceful Claude API failure, hot FAISS reload, standards-compliant CSV | Error handling in RAG Lambda, S3 versioned index, CSV generation conformance |
| Reliability | NFR25-NFR27: Zero data loss, logging works without LLM, idempotent IaC | DynamoDB durability guarantees, architectural separation of logging/AI paths, IaC state management |

**Scale & Complexity:**

- Primary domain: Full-stack serverless web app (SPA + AWS serverless backend)
- Complexity level: Medium — standard AWS components, novel RAG combination
- Estimated architectural components: ~12-15 (CloudFront + S3 static, API Gateway, 6-8 Lambda functions, DynamoDB tables, FAISS index on S3, Cognito, IaC stack)

### Technical Constraints & Dependencies

1. **AWS Free Tier ceiling** — capstone must run at $0. Architecture must minimize always-on resources (no NAT Gateways, no RDS, no ECS).
2. **Lambda memory limit for FAISS** — index file must load within 128-512MB Lambda allocation. Current corpus (13 XLSX cycles + 3-5 books) is small, but this constrains knowledge base growth.
3. **Lambda cold start + FAISS load** — first query after cold start may add 3-5s. Acceptable for async coaching but must be monitored (NFR2: 10s total).
4. **Single Claude API dependency** — all AI coaching depends on Claude API availability. Logging path must be fully independent (NFR26).
5. **7-day build constraint** — architecture must prioritize simplicity and standard patterns. No custom orchestration, no multi-step agents, no complex event-driven pipelines.
6. **Frontend framework flexibility** — PRD allows React, Preact, or vanilla JS. Architecture should not constrain this Day 6 decision.
7. **Local development parity** — the entire stack must run on a laptop with no AWS account. DynamoDB Local (Docker), FAISS on local filesystem, Flask/FastAPI serving the API, Vite for frontend, same Claude API key. Handler code is framework-agnostic with thin Lambda/Flask adapter layers. Environment-based config switching (local vs. AWS) via env vars, not code branches.

### Cross-Cutting Concerns Identified

1. **Authentication & Authorization** — Cognito JWT required on all 9 API endpoints. Must support tier-based access (free/premium) for rate limiting.
2. **Rate Limiting** — Per-user daily query counts across /query and /analyze endpoints. Three tiers: 3/day free, 10/day onboarding (first 7 days), unlimited premium. Must be server-side enforced (NFR12).
3. **Input Sanitization** — All user-facing text (chat queries, notes, program analysis) must be sanitized before LLM prompt injection. Maximum lengths enforced (2000 chars queries, 500 chars notes).
4. **Cost Tracking** — LLM query costs must be trackable per-user for both operational monitoring and future billing. Simple counter pattern in DynamoDB.
5. **Error Handling** — AI path failures must not affect logging path. Claude API outages return user-friendly messages. No cascading failures.
6. **IaC Completeness** — One-command deploy, one-command teardown, zero lingering resources. All infrastructure as code, no manual console steps.
7. **Environment Portability** — Every component must work identically in local dev and AWS production. Config-driven switching for: DynamoDB endpoint, FAISS index path, auth mode (real Cognito vs. local bypass), static file serving. No AWS-only code paths in business logic.

## Starter Template Evaluation

### Primary Technology Domain

Full-stack serverless web app — Python backend (FastAPI) + JavaScript SPA frontend (React) + AWS serverless deployment. No single starter template covers this combination; the stack is composed from standard scaffolds.

### Starter Options Considered

| Option | Evaluated For | Verdict |
|--------|--------------|---------|
| AWS SAM (`sam init`) v1.155.2 | IaC + Lambda scaffolding | Good for Lambda-focused apps, but CDK offers more flexibility for the full resource set (DynamoDB, ECR, CloudFront, Cognito) |
| AWS CDK (`cdk init`) v2.250.0 | IaC in Python | Selected — stays in Python, L2 constructs encode best practices, handles all AWS resources needed |
| Serverless Framework v4.34.0 | Alternative IaC | Rejected — proprietary licensing in v4, requires login, paid above $2M revenue |
| Vite 8.0.8 + React template | Frontend SPA scaffold | Selected — Rolldown bundler, hot reload, first-party Tailwind v4 plugin |
| Vite 8.0.8 + Preact template | Smaller bundle alternative | Considered — 3KB vs 40KB, but ecosystem/documentation advantage of React outweighs for a frontend newcomer |
| Vanilla JS + Vite | Minimal frontend | Rejected — manual state management for chat UI, logging form, and citation blocks is too costly in a 7-day build |

### Selected Approach: Composed Stack

**No single starter — two standard scaffolds + custom backend.**

**Frontend Initialization:**
```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install tailwindcss @tailwindcss/vite
```

**IaC Initialization:**
```bash
mkdir infra && cd infra
cdk init app --language python
```

**Backend:** Custom FastAPI project (no starter covers FastAPI + Mangum + DynamoDB + FAISS).

**Rationale:** The StrengthWise stack is a novel combination. Composing from standard parts gives full control without fighting an opinionated starter that doesn't match the architecture.

### Architectural Decisions Provided by This Approach

**Language & Runtime:**
- Backend + IaC: Python 3.12+
- Frontend: JavaScript/JSX (React)
- Single language for all server-side code

**API Framework:**
- FastAPI with Mangum v0.21.0 dual-mode adapter
- Local: `uvicorn main:app --reload`
- AWS: `handler = Mangum(app)` as Lambda entry point
- Same handler code, thin adapter layer at entry point

**Styling Solution:**
- Tailwind CSS v4 with first-party `@tailwindcss/vite` plugin
- No separate `tailwind.config.js` needed in v4
- Dark-first theme with Zinc base, Blue/Amber accent colors per UX spec

**Build Tooling:**
- Vite 8 (Rolldown bundler) for frontend — fast builds, HMR
- AWS CDK v2 in Python for infrastructure
- Docker for Lambda container image packaging (FAISS requires container deployment — exceeds ZIP size limits)

**Testing Framework:**
- pytest for backend (FastAPI TestClient for API tests)
- Vitest for frontend (native to Vite)

**Code Organization:**
```
strengthwise/
├── backend/           # FastAPI app, handlers, RAG pipeline
│   ├── main.py        # FastAPI app + Mangum handler
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/          # Vite + React + Tailwind SPA
├── infra/             # AWS CDK stacks (Python)
├── scripts/           # dev.sh, deploy.sh, seed.sh
└── Makefile           # make dev-backend, make dev-frontend, make deploy
```

**Development Experience:**
- Three terminals: uvicorn (backend), vite dev (frontend), DynamoDB Local (Docker)
- `scripts/dev.sh` starts the full local stack
- Environment config via `os.environ` with sane defaults — `.env` locally, Lambda env vars via CDK
- Separate Python venvs for backend/ and infra/ (different dependency trees)

**Note:** Project initialization using these commands should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- DynamoDB table design and access patterns
- Dual-mode backend pattern (FastAPI + Mangum)
- FAISS embedding model selection
- Authentication flow (Cognito JWT)
- Rate limiting mechanism

**Important Decisions (Shape Architecture):**
- Frontend state management approach
- Error handling standards
- Environment configuration pattern
- Container image build strategy

**Deferred Decisions (Post-MVP):**
- Caching strategy (not needed at capstone scale)
- CI/CD pipeline (manual deploy via CDK for MVP)
- Premium tier billing integration (Stripe — v2)
- XLSX import parsing strategy (v2)

### Data Architecture

**Database:** DynamoDB (on-demand capacity mode)

**Table Design:** Multi-table for simplicity and build speed.

| Table | PK | SK | Purpose |
|-------|----|----|---------|
| `Sessions` | `userId` (S) | `sessionDate#sessionId` (S) | Training session data — exercises, sets, reps, weight, RPE, notes |
| `QueryUsage` | `userId` (S) | `date` (S) | Daily AI query counter for rate limiting per user |
| `Feedback` | `queryId` (S) | — | Thumbs up/down on AI responses |

**Access Patterns:**
- Get all sessions for a user (sorted by date) — Sessions table, query on PK
- Get sessions in date range — Sessions table, query on PK + SK begins_with/between
- Get today's query count — QueryUsage table, get item
- Log feedback — Feedback table, put item

**Exercise Database:** Static JSON file bundled with the backend (not DynamoDB). Pre-populated sport-specific exercises for grip, armwrestling, powerlifting, general strength. Loaded at startup, served from memory. No write operations needed — only the operator updates exercises.

**Data Validation:** Pydantic models in FastAPI for all request/response schemas. Validates types, enforces max lengths (2000 chars queries, 500 chars notes), sanitizes input before LLM context injection.

**Embedding Model:** `all-MiniLM-L6-v2` via sentence-transformers. Free, local, no external API dependency. ~80MB model size added to container image. Generates 384-dimensional embeddings for FAISS index. Same model runs locally and on Lambda.

### Authentication & Security

**Authentication:** AWS Cognito user pools with email-based registration. JWT tokens on all API endpoints.

**Auth Flow:**
- Frontend: Cognito Hosted UI or Amplify Auth library for sign-up/sign-in
- Backend: JWT verification middleware in FastAPI
- Local dev: Auth middleware bypassed, injects test user ID from `.env`

**Authorization:** Tier-based access derived from user attributes in Cognito (free/onboarding/premium). Rate limiting enforced server-side per user.

**Input Sanitization:** All user-facing text fields (chat queries, notes, program analysis) sanitized before inclusion in LLM prompts. Strip injection patterns, enforce max lengths, escape special characters. Implemented as FastAPI middleware.

**API Security:** HTTPS enforced by API Gateway and CloudFront (default). No unauthenticated endpoints except health check.

### API & Communication Patterns

**API Style:** REST (defined in PRD — 9 endpoints, all Cognito JWT authenticated).

**Error Response Format:** Consistent JSON structure across all endpoints:
```json
{
  "error": "human_readable_message",
  "code": "ERROR_CODE",
  "detail": {}
}
```

**Rate Limiting:** DynamoDB-based counter in `QueryUsage` table. On each `/query` or `/analyze` request:
1. Read today's count for user
2. Check against tier limit (3/day free, 10/day onboarding first 7 days, unlimited premium)
3. If under limit: increment and proceed. If over: return 429 with reset time.
Atomic update via DynamoDB `UpdateItem` with condition expression — no race conditions.

**CORS:** FastAPI `CORSMiddleware` — works identically in local dev (uvicorn) and on Lambda (Mangum). Allows frontend origin only.

**API Documentation:** FastAPI auto-generates OpenAPI spec at `/docs`. Available in local dev, disabled in production.

### Frontend Architecture

**Framework:** React (via Vite 8 + `react` template)

**State Management:** `useState` + `fetch`. No state library. Sufficient for 4 screens with independent data needs. Chat message history held in component state; cleared on page refresh (acceptable for MVP).

**Routing:** React Router v7. Four routes: `/` (dashboard), `/log` (logging form), `/chat` (coaching), `/history` (session list). Client-side routing with hash or browser history.

**Data Fetching:** Native `fetch` API with a thin wrapper (`api.js`) that handles:
- Cognito JWT token attachment
- Base URL switching (local vs. API Gateway)
- Error response parsing
- Loading/error state helpers

**Performance:** Tailwind CSS v4 purges unused CSS. No code splitting needed for 4 screens. System font stack (no font loading). Vite's Rolldown produces optimized production bundles.

### Infrastructure & Deployment

**Hosting:**
- Frontend: S3 bucket + CloudFront distribution (CDK manages both)
- Backend: Lambda (container image from ECR) + API Gateway
- Auth: Cognito user pool
- Data: DynamoDB tables (on-demand)
- Vector store: FAISS index file in S3, downloaded to `/tmp` on Lambda cold start

**IaC:** AWS CDK v2 in Python. Single stack for all resources. `cdk deploy` / `cdk destroy` for one-command operations.

**Container Build:** Dockerfile in `backend/`. Multi-stage build:
1. Stage 1: Install Python deps (faiss-cpu, sentence-transformers, FastAPI, boto3, anthropic, mangum)
2. Stage 2: Copy app code + deps into Lambda base image
3. Target: `--platform linux/amd64` (required even on Apple Silicon)

**Environment Configuration:** Single `config.py` reading from `os.environ` with defaults:
```python
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # None for AWS, "http://localhost:8000" for local
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")  # local path or S3 key
AUTH_BYPASS = os.getenv("AUTH_BYPASS", "false")  # "true" for local dev
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250514")
```

**Monitoring:** CloudWatch (Lambda logs, API Gateway metrics, DynamoDB capacity). No custom dashboards for MVP — AWS Console direct access.

**Scaling:** Lambda auto-scales. DynamoDB on-demand auto-scales. No manual scaling config needed. FAISS index loaded per Lambda instance — stateless.

### Decision Impact Analysis

**Implementation Sequence:**
1. Project scaffold (backend/, frontend/, infra/, scripts/, Makefile)
2. CDK stack with DynamoDB tables + Cognito
3. FastAPI app with health endpoint + Mangum adapter
4. DynamoDB integration (sessions CRUD)
5. FAISS index build (sentence-transformers + knowledge corpus)
6. RAG pipeline (FAISS search + DynamoDB fetch + Claude API call)
7. Frontend scaffold (Vite + React + Tailwind + React Router)
8. Frontend screens (logging form, chat, dashboard, history)
9. Container build + ECR push + Lambda deployment
10. CloudFront + S3 frontend deployment

**Cross-Component Dependencies:**
- Rate limiting depends on: DynamoDB QueryUsage table + auth middleware (user ID extraction)
- RAG pipeline depends on: FAISS index (embedding model) + DynamoDB sessions table + Claude API
- Frontend data fetching depends on: auth token management + API base URL config
- Container deployment depends on: all backend dependencies finalized (FAISS, sentence-transformers, etc.)

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Database Naming (DynamoDB):**
- Table names: PascalCase — `Sessions`, `QueryUsage`, `Feedback`
- Attribute names: camelCase — `userId`, `sessionDate`, `exerciseName`, `queryCount`
- Partition/Sort key attributes: camelCase — `userId`, `sessionDate#sessionId`

**API Naming:**
- Endpoints: lowercase plural nouns — `/sessions`, `/exercises`, `/profile`
- Route parameters: `{id}` format — `/sessions/{id}`
- Query parameters: camelCase — `?sportType=grip&startDate=2026-04-01`
- JSON request/response fields: camelCase — `{ "userId": "...", "exerciseName": "..." }`
- FastAPI Pydantic models use `alias_generator = to_camel` to bridge Python snake_case internals to camelCase API output

**Python Code (backend/):**
- Variables/functions: snake_case — `get_user_sessions()`, `query_count`
- Classes: PascalCase — `SessionModel`, `RagPipeline`
- Files/modules: snake_case — `rag_pipeline.py`, `session_service.py`
- Constants: UPPER_SNAKE — `MAX_QUERY_LENGTH = 2000`

**JavaScript/React Code (frontend/):**
- Variables/functions: camelCase — `fetchSessions()`, `queryCount`
- Components: PascalCase — `CitationBlock`, `SetEntryRow`, `ChatBubble`
- Component files: PascalCase — `CitationBlock.jsx`, `SetEntryRow.jsx`
- Utility files: camelCase — `api.js`, `auth.js`
- CSS classes: Tailwind utilities only (no custom class naming)
- Constants: UPPER_SNAKE — `API_BASE_URL`

### Structure Patterns

**Project Organization:**
```
backend/
├── main.py              # FastAPI app + Mangum handler
├── config.py            # Environment config
├── routers/             # FastAPI route modules
│   ├── sessions.py
│   ├── query.py
│   ├── exercises.py
│   └── profile.py
├── services/            # Business logic
│   ├── session_service.py
│   ├── rag_service.py
│   └── rate_limit_service.py
├── models/              # Pydantic request/response models
├── middleware/           # Auth, CORS, input sanitization
├── data/                # Exercise database JSON, FAISS index (local)
├── tests/               # pytest tests mirror src structure
│   ├── test_sessions.py
│   ├── test_rag.py
│   └── conftest.py
├── Dockerfile
├── requirements.txt
└── .env

frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── api.js           # Fetch wrapper with auth
│   ├── pages/           # Route-level components
│   │   ├── Dashboard.jsx
│   │   ├── LogSession.jsx
│   │   ├── Chat.jsx
│   │   └── History.jsx
│   ├── components/      # Shared UI components
│   │   ├── TabBar.jsx
│   │   ├── CitationBlock.jsx
│   │   ├── SetEntryRow.jsx
│   │   ├── ExercisePicker.jsx
│   │   ├── FollowupChip.jsx
│   │   └── SessionCard.jsx
│   └── index.css        # Tailwind import
├── index.html
└── vite.config.js
```

**Convention:** Pages are route-level containers. Components are reusable UI pieces. Services contain business logic. Routers are thin — validate input, call service, return response.

### Format Patterns

**API Response Formats:**

Success:
```json
{
  "data": { ... }
}
```

Error:
```json
{
  "error": "Human-readable message",
  "code": "RATE_LIMIT_EXCEEDED",
  "detail": { "resetAt": "2026-04-20T00:00:00Z", "limit": 3 }
}
```

AI coaching response:
```json
{
  "data": {
    "response": "Coaching text with citations...",
    "citations": {
      "personal": [
        { "sessionDate": "2026-04-15", "exercise": "Gripper close", "detail": "4x3 @ 80kg, RPE 9" }
      ],
      "knowledge": [
        { "source": "Prilepin's Chart", "principle": "For >90% intensity, 4-10 total reps optimal" }
      ]
    },
    "confidence": "medium",
    "queriesRemaining": 2
  }
}
```

**Date/Time:** ISO 8601 strings in all JSON — `"2026-04-20T14:30:00Z"`. Frontend formats for display.

**Null Handling:** Omit null fields from JSON responses. Use `exclude_none=True` in Pydantic serialization.

**HTTP Status Codes:**
- 200: Success (GET, PUT)
- 201: Created (POST /sessions)
- 400: Validation error
- 401: Not authenticated
- 403: Not authorized
- 404: Not found
- 429: Rate limit exceeded
- 500: Server error (never expose internals)

### Process Patterns

**Error Handling:**
- Backend: FastAPI exception handlers return consistent error JSON. Never expose stack traces in production. Log full errors to CloudWatch.
- Frontend: `api.js` wrapper catches errors and returns `{ data: null, error: { message, code } }`. Components check `error` before rendering.
- AI query failures: Return friendly message — "I couldn't process that question right now. Please try again." Never show raw LLM errors.
- Logging path independent: If Claude API is down, `/sessions` endpoints still work (NFR26).

**Loading States:**
- Frontend uses boolean `isLoading` per fetch operation
- Chat: "StrengthWise is thinking..." with pulsing dots (CSS animation)
- Session save: Button shows spinner, keeps size (no layout shift)
- Initial page load: Skeleton screens (Zinc-800 blocks with pulse animation)
- Convention: Every fetch call has three states: idle, loading, done/error

**Auth Pattern:**
- Frontend: Store Cognito JWT in memory (not localStorage). Refresh on expiry via Cognito SDK.
- Backend middleware: Extract user ID from JWT `sub` claim. Inject into request context.
- Local dev: `AUTH_BYPASS=true` → middleware injects `TEST_USER_ID` from `.env`.

**Input Sanitization Pattern:**
- All `/query` and `/analyze` inputs pass through `sanitize_llm_input()` before hitting the LLM prompt
- Strip common injection patterns, enforce max length, escape delimiters
- Sanitization happens in the service layer, not the router

### Enforcement Guidelines

**All AI Agents MUST:**
1. Follow camelCase for all JSON API fields — no snake_case leaks from Python
2. Use the `api.js` wrapper for all frontend fetch calls — never raw `fetch` with manual auth headers
3. Put business logic in `services/`, not in `routers/` — routers are thin
4. Return the standard error JSON format for all error responses — no ad-hoc error shapes
5. Use Pydantic models for all request/response validation — no manual dict checking
6. Keep the logging path (sessions CRUD) completely independent of the AI path (query/analyze)

**Anti-Patterns to Avoid:**
- Putting DynamoDB calls directly in router functions (use services)
- Mixing snake_case and camelCase in the same JSON response
- Hardcoding DynamoDB table names (use `config.py`)
- Catching and silencing exceptions without logging
- Creating new utility files for one-off functions (inline or add to existing module)
- Adding state management libraries (useState is sufficient)

## Project Structure & Boundaries

### Complete Project Directory Structure

```
strengthwise/
├── README.md
├── Makefile                          # make dev-backend, make dev-frontend, make deploy, make seed
├── .gitignore
├── .env.example                      # Template for local dev env vars
│
├── backend/
│   ├── main.py                       # FastAPI app + Mangum Lambda handler
│   ├── config.py                     # Environment config (os.environ with defaults)
│   ├── requirements.txt              # Production deps
│   ├── requirements-dev.txt          # pytest, httpx (test client)
│   ├── Dockerfile                    # Multi-stage Lambda container build
│   ├── .env                          # Local dev env vars (gitignored)
│   │
│   ├── routers/                      # FastAPI route modules (thin)
│   │   ├── __init__.py
│   │   ├── sessions.py               # POST/GET /sessions, GET /sessions/{id}
│   │   ├── query.py                  # POST /query (dual-source RAG)
│   │   ├── analyze.py                # POST /analyze (program analysis)
│   │   ├── exercises.py              # GET /exercises
│   │   ├── profile.py                # GET /profile
│   │   ├── export.py                 # POST /export (CSV)
│   │   └── account.py                # DELETE /account
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── session_service.py        # CRUD for training sessions
│   │   ├── rag_service.py            # Dual-source RAG pipeline (FAISS + DynamoDB + Claude)
│   │   ├── rate_limit_service.py     # Query counting and tier enforcement
│   │   ├── exercise_service.py       # Exercise database lookup
│   │   ├── export_service.py         # CSV generation
│   │   └── account_service.py        # Account deletion (cascading data removal)
│   │
│   ├── models/                       # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── session_models.py         # SessionCreate, SessionResponse, ExerciseEntry, SetEntry
│   │   ├── query_models.py           # QueryRequest, QueryResponse, Citation, CoachingResponse
│   │   ├── exercise_models.py        # Exercise, ExerciseList
│   │   ├── profile_models.py         # UserProfile, UsageStats
│   │   └── common.py                 # ErrorResponse, SuccessResponse wrappers
│   │
│   ├── middleware/                    # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── auth.py                   # Cognito JWT verification (bypass mode for local dev)
│   │   └── sanitize.py               # Input sanitization for LLM-facing text
│   │
│   ├── data/                         # Static data and local FAISS index
│   │   ├── exercises.json            # Pre-populated sport-specific exercise database
│   │   ├── faiss_index/              # FAISS index files (local dev)
│   │   │   ├── index.faiss
│   │   │   └── index_metadata.json   # Chunk-to-source mapping
│   │   └── knowledge/                # Source knowledge base documents
│   │       ├── periodization.md
│   │       ├── prilepin.md
│   │       └── ...
│   │
│   ├── scripts/                      # Backend-specific scripts
│   │   ├── build_faiss_index.py      # Embed knowledge corpus → FAISS index
│   │   ├── seed_demo_data.py         # Seed 30+ demo sessions for capstone
│   │   └── upload_index_to_s3.py     # Push FAISS index to S3 for Lambda
│   │
│   └── tests/                        # pytest — mirrors routers/services structure
│       ├── __init__.py
│       ├── conftest.py               # Fixtures: test client, mock DynamoDB, test user
│       ├── test_sessions.py
│       ├── test_query.py
│       ├── test_rate_limit.py
│       └── test_sanitize.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                # Vite 8 config + Tailwind plugin
│   ├── src/
│   │   ├── main.jsx                  # React entry point + router setup
│   │   ├── App.jsx                   # Root component (layout + tab bar/sidebar)
│   │   ├── index.css                 # @import "tailwindcss" + custom tokens
│   │   ├── api.js                    # Fetch wrapper (auth, base URL, error handling)
│   │   ├── auth.js                   # Cognito auth helper (token management)
│   │   │
│   │   ├── pages/                    # Route-level containers
│   │   │   ├── Dashboard.jsx
│   │   │   ├── LogSession.jsx
│   │   │   ├── Chat.jsx
│   │   │   └── History.jsx
│   │   │
│   │   └── components/               # Reusable UI components
│   │       ├── TabBar.jsx
│   │       ├── HeaderBar.jsx
│   │       ├── SessionCard.jsx
│   │       ├── ExerciseBlock.jsx
│   │       ├── SetEntryRow.jsx
│   │       ├── ExercisePicker.jsx
│   │       ├── SportSelector.jsx
│   │       ├── ChatBubble.jsx
│   │       ├── CitationBlock.jsx
│   │       ├── FollowupChip.jsx
│   │       ├── QueryCounter.jsx
│   │       ├── FeedbackButtons.jsx
│   │       ├── SkeletonScreen.jsx
│   │       └── ErrorInline.jsx
│   │
│   └── public/
│
├── infra/
│   ├── app.py                        # CDK entry point
│   ├── cdk.json
│   ├── requirements.txt              # CDK + boto3 deps
│   ├── stacks/
│   │   └── strengthwise_stack.py     # Single stack: all AWS resources
│   └── .env                          # AWS account/region config (gitignored)
│
└── scripts/
    ├── dev.sh                        # Start full local stack
    ├── deploy.sh                     # Build + push + cdk deploy
    ├── teardown.sh                   # cdk destroy + cleanup
    └── seed.sh                       # Run demo data seeding
```

### Architectural Boundaries

**API Boundaries (9 endpoints):**

| Endpoint | Router | Service | DynamoDB Table | LLM |
|----------|--------|---------|----------------|-----|
| POST /sessions | sessions.py | session_service | Sessions | No |
| GET /sessions | sessions.py | session_service | Sessions | No |
| GET /sessions/{id} | sessions.py | session_service | Sessions | No |
| POST /query | query.py | rag_service + rate_limit_service | Sessions + QueryUsage | Yes |
| POST /analyze | analyze.py | rag_service + rate_limit_service | Sessions + QueryUsage | Yes |
| GET /exercises | exercises.py | exercise_service | None (static JSON) | No |
| GET /profile | profile.py | session_service + rate_limit_service | Sessions + QueryUsage | No |
| POST /export | export.py | export_service | Sessions | No |
| DELETE /account | account.py | account_service | All tables (cascade) | No |

**Service Boundaries:**
- `session_service` — owns Sessions table reads/writes. No LLM dependency.
- `rag_service` — owns the RAG pipeline: FAISS search → DynamoDB personal data fetch → Claude API call → citation formatting. The only service that touches the LLM.
- `rate_limit_service` — owns QueryUsage table. Called by query/analyze routers before rag_service.
- `exercise_service` — owns static exercises.json. Read-only, loaded at startup.

**Data Boundaries:**
- Each service owns its DynamoDB table(s) — no direct cross-table queries between services
- `rag_service` calls `session_service.get_user_sessions()` to fetch personal data for RAG context — it does not query DynamoDB directly
- FAISS index is loaded once per Lambda instance (cold start) or at FastAPI startup (local dev)

### Requirements to Structure Mapping

| FR Category | Routers | Services | Frontend Pages | Components |
|-------------|---------|----------|----------------|------------|
| Session Logging (FR1-FR7) | sessions.py | session_service | LogSession, History | ExerciseBlock, SetEntryRow, ExercisePicker, SportSelector, SessionCard |
| AI Coaching (FR8-FR14) | query.py, analyze.py | rag_service | Chat | ChatBubble, CitationBlock, FollowupChip, FeedbackButtons |
| Rate Limiting (FR15-FR18) | query.py, analyze.py | rate_limit_service | Chat | QueryCounter |
| Account Mgmt (FR19-FR23) | profile.py, export.py, account.py | export_service, account_service | (settings — post-MVP) | — |
| Knowledge Base (FR24-FR26) | exercises.py | exercise_service, rag_service | LogSession | ExercisePicker |
| Safety (FR27-FR33) | all routers | middleware/sanitize.py | Chat (disclaimer) | ErrorInline |

### Data Flow

**Logging Flow (no LLM — $0 cost):**
```
Frontend LogSession.jsx
  → api.js (attach JWT)
  → POST /sessions
  → auth middleware (verify JWT, extract userId)
  → sessions router (validate via Pydantic)
  → session_service.create_session()
  → DynamoDB Sessions table (put_item)
  → 201 response
```

**AI Coaching Flow (LLM — ~$0.01-0.05 per query):**
```
Frontend Chat.jsx
  → api.js (attach JWT)
  → POST /query
  → auth middleware (verify JWT, extract userId)
  → query router (validate via Pydantic)
  → sanitize_llm_input(query_text)
  → rate_limit_service.check_and_increment(userId)
    → DynamoDB QueryUsage (conditional update)
    → if over limit: 429 response
  → rag_service.query(userId, query_text)
    → embed query (sentence-transformers)
    → FAISS search → top-K general knowledge chunks
    → session_service.get_user_sessions(userId, date_range)
    → build LLM prompt (query + personal data + general knowledge)
    → Claude API call
    → parse response into text + citations
  → 200 response with CoachingResponse
```

### Development Workflow

**Local Dev (3 terminals):**
1. `docker run -p 8000:8000 amazon/dynamodb-local` — DynamoDB Local
2. `cd backend && uvicorn main:app --reload --port 8080` — API server
3. `cd frontend && npm run dev` — Vite dev server (port 5173)

Or: `make dev` runs all three via `scripts/dev.sh`.

**Deployment:**
1. `docker build` backend container → push to ECR
2. `cd infra && cdk deploy` — provisions everything
3. `cd frontend && npm run build` → upload `dist/` to S3
4. CloudFront invalidation

Or: `make deploy` runs all via `scripts/deploy.sh`.

**Teardown:** `make teardown` → `cdk destroy` + ECR image cleanup.

## Architecture Validation Results

### Coherence Validation

- All technology choices verified compatible (FastAPI + Mangum + CDK + DynamoDB + FAISS + React + Vite 8 + Tailwind v4)
- Naming patterns consistent: camelCase JSON, snake_case Python, PascalCase React components
- Project structure supports all defined boundaries and patterns
- No contradictory decisions found

### Requirements Coverage

- **33/33 Functional Requirements** have architectural support
- **27/27 Non-Functional Requirements** addressed
- All 6 FR categories mapped to specific routers, services, pages, and components

### Implementation Readiness

- All critical decisions documented with versions
- Project tree is complete and specific
- Enforcement guidelines and anti-patterns defined
- Data flow diagrams cover both primary paths (logging and AI coaching)

### Gap Analysis

**Critical Gaps:** None

**Minor Gaps (addressed):**
- Onboarding tier detection: use Cognito `UserCreateDate` from JWT claims to determine if user is in first 7 days
- Chat history persistence: deferred to v2 (acceptable for MVP)
- FAISS hot reload: natural cold start rotation sufficient at capstone scale

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context analyzed with 33 FRs and 27 NFRs
- [x] Scale assessed: medium complexity, 100 concurrent users target
- [x] Technical constraints: AWS Free Tier, 7-day build, Lambda memory, local dev parity
- [x] Cross-cutting concerns: auth, rate limiting, sanitization, cost tracking, error handling, env portability

**Architectural Decisions**
- [x] Data architecture: DynamoDB multi-table with defined access patterns
- [x] Auth: Cognito JWT with tier-based access
- [x] API: REST, 9 endpoints, consistent error format, DynamoDB rate limiting
- [x] Frontend: React + Vite 8 + Tailwind v4, useState + fetch, React Router v7
- [x] Infrastructure: CDK, container Lambda (ECR), S3 + CloudFront
- [x] RAG: sentence-transformers (all-MiniLM-L6-v2) + FAISS + Claude API

**Implementation Patterns**
- [x] Naming conventions: database, API, Python, JavaScript
- [x] Structure patterns: routers → services → DynamoDB, pages → components
- [x] Format patterns: API responses, dates, HTTP codes, null handling
- [x] Process patterns: error handling, loading states, auth, sanitization
- [x] Enforcement guidelines and anti-patterns

**Project Structure**
- [x] Complete directory tree with all files
- [x] 9 API endpoints mapped to routers and services
- [x] FR-to-structure mapping table
- [x] Data flow diagrams for logging and AI coaching paths
- [x] Development workflow (local + deploy + teardown)

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Clean separation of logging (free) and AI coaching (paid) paths
- Full local dev parity — no AWS account needed to develop
- Every FR and NFR has an architectural home
- Dual-mode FastAPI/Lambda pattern is proven and simple
- Cost-conscious design: $0 at capstone, bounded at scale

**Areas for Future Enhancement:**
- Chat history persistence (v2)
- XLSX import pipeline (v2)
- Proactive pattern detection (v2)
- Premium billing integration (v2)
- CI/CD pipeline (manual deploy acceptable for MVP)

### Implementation Handoff

**First implementation priority:** Project scaffold — create directory structure, initialize Vite + React frontend, FastAPI backend with `/health` endpoint, CDK stack with DynamoDB tables. Validate the local dev loop (uvicorn + DynamoDB Local + vite dev) before building any features.
