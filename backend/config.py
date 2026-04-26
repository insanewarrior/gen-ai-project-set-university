import os

DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
AUTH_BYPASS = os.getenv("AUTH_BYPASS", "false")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
TEST_USER_ID = os.getenv("TEST_USER_ID", "test-user-001")
TEST_USER_CREATE_DATE = os.getenv("TEST_USER_CREATE_DATE", "2025-01-01T00:00:00")
TEST_IS_PREMIUM = os.getenv("TEST_IS_PREMIUM", "false")

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
