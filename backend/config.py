import os

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
AUTH_BYPASS = os.getenv("AUTH_BYPASS", "false")
CLAUDE_MODEL = os.getenv(
    "CLAUDE_MODEL", "claude-sonnet-4-5-20250514"
)
TEST_USER_ID = os.getenv("TEST_USER_ID", "test-user-001")

SESSIONS_TABLE_NAME = os.getenv(
    "SESSIONS_TABLE_NAME", "Sessions"
)
QUERY_USAGE_TABLE_NAME = os.getenv(
    "QUERY_USAGE_TABLE_NAME", "QueryUsage"
)
FEEDBACK_TABLE_NAME = os.getenv(
    "FEEDBACK_TABLE_NAME", "Feedback"
)
S3_FAISS_BUCKET = os.getenv("S3_FAISS_BUCKET")
