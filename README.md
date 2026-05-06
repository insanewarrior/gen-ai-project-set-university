# StrengthWise

Cross-domain AI strength coach with memory — dual-source RAG + structured logging.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for DynamoDB Local)
- AWS CDK CLI (`npm install -g aws-cdk`) — required for deployment only, not for local dev

## Local Development Setup

1. Clone the repository and navigate to the project root.

2. Set up the backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   cp .env.example .env
   cd ..
   ```

   > **Required:** open `backend/.env` and set `GOOGLE_API_KEY` to your Google AI Studio key.
   > All other values work as-is for local development.

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Start all services:
   ```bash
   make dev
   ```

   This starts:
   - DynamoDB Local on port 8000
   - FastAPI backend on port 8080
   - Vite dev server on port 5173

5. Seed the local database with realistic training sessions:
   ```bash
   make seed        # create DynamoDB tables
   make seed-data   # insert sessions for all three dev users
   ```

6. Open http://localhost:5173 in your browser.

> **Note:** The FAISS knowledge base index is pre-built and committed to the repo — no need to run `make build-index` for a fresh clone. Only run it if you modify files under `backend/data/knowledge/`.

## Project Structure

```
├── backend/       # FastAPI + Mangum (runs on Lambda)
├── frontend/      # Vite + React + Tailwind CSS v4
├── infra/         # AWS CDK (Python)
├── scripts/       # Dev and deployment scripts
└── Makefile       # Task runner
```

## Dev Users

In local development (`AUTH_BYPASS=true`) three users are available via the `x-dev-user` request header. Each has a pre-seeded training history after running `make seed-data`:

| Header value | User ID | Tier | Sessions | Story |
|---|---|---|---|---|
| `x-dev-user: free` | `test-user-free` | Free | 5 | Grip only — AI gives low-confidence responses |
| `x-dev-user: onboarding` | `test-user-onboarding` | Free (new) | 12 | Grip + armwrestling — medium confidence |
| `x-dev-user: premium` | `test-user-premium` | Premium | 60 | All sports, RPE stall + deload cycle — high confidence, pattern detection |

The default user (no header) is controlled by `TEST_USER_ID` / `TEST_IS_PREMIUM` in `backend/.env`.

## Makefile Targets

| Target | Description |
|---|---|
| `make dev` | Start all local services (DynamoDB, backend, frontend) |
| `make dev-backend` | Start backend only |
| `make dev-frontend` | Start frontend only |
| `make seed` | Create DynamoDB tables |
| `make seed-data` | Insert training sessions for all three dev users |
| `make seed-data-fresh` | Wipe and re-insert seed data (clean slate) |
| `make build-index` | Rebuild FAISS knowledge base index |
| `make upload-index` | Upload FAISS index to S3 (requires `S3_BUCKET`) |
| `make update-kb` | Rebuild + upload index |
| `make deploy` | Deploy to AWS via CDK |
| `make teardown` | Tear down AWS stack |

## Environment Variables

See `backend/.env.example` for all configuration options. The root `.env.example` is a reference for deployment variables only.
