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

5. Open http://localhost:5173 in your browser.

> **Note:** The FAISS knowledge base index is pre-built and committed to the repo — no need to run `make build-index` for a fresh clone. Only run it if you modify files under `backend/data/knowledge/`.

## Project Structure

```
├── backend/       # FastAPI + Mangum (runs on Lambda)
├── frontend/      # Vite + React + Tailwind CSS v4
├── infra/         # AWS CDK (Python)
├── scripts/       # Dev and deployment scripts
└── Makefile       # Task runner
```

## Makefile Targets

| Target         | Description                        |
|----------------|------------------------------------|
| `make dev`          | Start all local services           |
| `make dev-backend`  | Start backend only                 |
| `make dev-frontend` | Start frontend only                |
| `make build-index`  | Build FAISS knowledge base index   |
| `make deploy`       | Deploy to AWS (placeholder)        |
| `make seed`         | Seed local database (placeholder)  |

## Environment Variables

See `backend/.env.example` for all configuration options. The root `.env.example` is a reference for deployment variables only.
