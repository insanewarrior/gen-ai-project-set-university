# StrengthWise

Cross-domain AI strength coach with memory — dual-source RAG + structured logging.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for DynamoDB Local)
- AWS CDK CLI (`npm install -g aws-cdk`)

## Local Development Setup

1. Clone the repository and navigate to the project root.

2. Set up the backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   cp .env.example .env  # adjust values as needed
   cd ..
   ```

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
| `make dev`     | Start all local services           |
| `make dev-backend`  | Start backend only            |
| `make dev-frontend` | Start frontend only           |
| `make deploy`  | Deploy to AWS (placeholder)        |
| `make seed`    | Seed local database (placeholder)  |

## Environment Variables

See `.env.example` for all configuration options.
