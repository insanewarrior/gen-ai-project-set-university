"""
Session endpoint tests for Story 2.2.

All auth-passing tests use AUTH_BYPASS=true via monkeypatch.
DynamoDB is mocked per-test with @mock_aws decorator.
"""
import os

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

import config
import middleware.auth as auth_module


# ---------------------------------------------------------------------------
# AWS credential setup
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sessions_table():
    import importlib
    importlib.reload(config)  # reset after test_config_from_env pollution
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    return dynamodb.create_table(
        TableName=config.SESSIONS_TABLE_NAME,
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'},
            {'AttributeName': 'sk', 'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'},
            {'AttributeName': 'sk', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST',
    )


def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    from main import app
    return TestClient(app)


SAMPLE_PAYLOAD = {
    "sessionDate": "2026-04-25",
    "sport": "grip",
    "exercises": [
        {
            "exerciseId": "grip-gripper-close",
            "exerciseName": "Gripper Close",
            "sportType": "grip",
            "sets": [
                {"setNumber": 1, "weight": 80.0, "reps": 3, "rpe": 9.0}
            ],
        }
    ],
    "notes": None,
}


# ---------------------------------------------------------------------------
# POST /sessions — success
# ---------------------------------------------------------------------------


@mock_aws
def test_post_session_returns_201(monkeypatch):
    """POST /sessions → 201, response has data.session.sessionId."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    response = client.post("/sessions", json=SAMPLE_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert "sessionId" in body["data"]["session"]
    assert body["data"]["monthCount"] == 1


@mock_aws
def test_post_session_month_count_increments(monkeypatch):
    """POST /sessions twice → second response has monthCount == 2."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    client.post("/sessions", json=SAMPLE_PAYLOAD)
    response2 = client.post("/sessions", json=SAMPLE_PAYLOAD)
    assert response2.status_code == 201
    assert response2.json()["data"]["monthCount"] == 2


# ---------------------------------------------------------------------------
# GET /sessions
# ---------------------------------------------------------------------------


@mock_aws
def test_get_sessions_returns_list(monkeypatch):
    """GET /sessions after 2 POSTs → 200, data.sessions has 2 items."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    payload1 = {**SAMPLE_PAYLOAD, "sessionDate": "2026-04-24"}
    payload2 = {**SAMPLE_PAYLOAD, "sessionDate": "2026-04-25"}
    client.post("/sessions", json=payload1)
    client.post("/sessions", json=payload2)
    response = client.get("/sessions")
    assert response.status_code == 200
    sessions = response.json()["data"]["sessions"]
    assert len(sessions) == 2
    # Newest first (ScanIndexForward=False) — SK starts with date
    assert sessions[0]["sessionDate"] >= sessions[1]["sessionDate"]


# ---------------------------------------------------------------------------
# GET /sessions/{id}
# ---------------------------------------------------------------------------


@mock_aws
def test_get_session_by_id(monkeypatch):
    """GET /sessions/{id}?session_date=... → 200 with correct session."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    post_response = client.post("/sessions", json=SAMPLE_PAYLOAD)
    session_id = post_response.json()["data"]["session"]["sessionId"]
    session_date = SAMPLE_PAYLOAD["sessionDate"]
    url = f"/sessions/{session_id}?session_date={session_date}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()["data"]["session"]["sessionId"] == session_id


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


def test_post_session_requires_auth(monkeypatch):
    """POST /sessions without auth → 401 when AUTH_BYPASS=false."""
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    monkeypatch.setattr(config, "AUTH_BYPASS", "false")
    from main import app
    client = TestClient(app)
    response = client.post("/sessions", json=SAMPLE_PAYLOAD)
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Pydantic validation
# ---------------------------------------------------------------------------


@mock_aws
def test_post_session_notes_too_long(monkeypatch):
    """POST /sessions with notes > 500 chars → 422."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    bad_payload = {**SAMPLE_PAYLOAD, "notes": "x" * 501}
    response = client.post("/sessions", json=bad_payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# camelCase assertions
# ---------------------------------------------------------------------------


@mock_aws
def test_response_uses_camel_case(monkeypatch):
    """Session response uses camelCase keys (sessionDate, exerciseId)."""
    _make_sessions_table()
    client = _bypass_client(monkeypatch)
    response = client.post("/sessions", json=SAMPLE_PAYLOAD)
    assert response.status_code == 201
    session = response.json()["data"]["session"]
    assert "sessionDate" in session, "sessionDate key missing"
    assert "session_date" not in session, "snake_case leaked"
    exercises = session["exercises"]
    assert len(exercises) > 0
    assert "exerciseId" in exercises[0], "exerciseId key missing"
