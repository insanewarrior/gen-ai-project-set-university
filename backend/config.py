import os

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # None for AWS, "http://localhost:8000" for local
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
AUTH_BYPASS = os.getenv("AUTH_BYPASS", "false")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250514")
TEST_USER_ID = os.getenv("TEST_USER_ID", "test-user-001")
