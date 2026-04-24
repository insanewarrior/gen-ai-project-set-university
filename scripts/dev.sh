#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Start DynamoDB Local if not already running
if ! docker ps --format '{{.Names}}' | grep -q '^dynamodb-local$'; then
  echo "Starting DynamoDB Local..."
  docker run -d --name dynamodb-local -p 8000:8000 amazon/dynamodb-local 2>/dev/null || \
    docker start dynamodb-local
else
  echo "DynamoDB Local already running."
fi

# Start backend
echo "Starting FastAPI backend on port 8080..."
(cd "$PROJECT_ROOT/backend" && source .venv/bin/activate && uvicorn main:app --reload --port 8080) &
BACKEND_PID=$!

# Start frontend
echo "Starting Vite dev server on port 5173..."
(cd "$PROJECT_ROOT/frontend" && npm run dev) &
FRONTEND_PID=$!

# Trap to clean up child processes on exit
cleanup() {
  echo ""
  echo "Shutting down services..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo "Services stopped."
}
trap cleanup EXIT INT TERM

echo ""
echo "All services started:"
echo "  DynamoDB Local: http://localhost:8000"
echo "  Backend API:    http://localhost:8080"
echo "  Frontend:       http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services."

wait
