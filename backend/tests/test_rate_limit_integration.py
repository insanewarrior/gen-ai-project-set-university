"""Integration tests for rate limiting at the endpoint level."""
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import config
import middleware.auth as auth_module


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    monkeypatch.setattr(config, "TEST_USER_CREATE_DATE", "2025-01-01T00:00:00")
    monkeypatch.setattr(config, "TEST_IS_PREMIUM", "false")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)


_MOCK_RATE_DENIED = {
    "allowed": False,
    "queries_remaining": 0,
    "tier_limit": 3,
    "reset_at": "2026-04-27T00:00:00Z",
}
_MOCK_RATE_ALLOWED = {
    "allowed": True,
    "queries_remaining": 2,
    "tier_limit": 3,
    "reset_at": "2026-04-27T00:00:00Z",
}
_MOCK_RAG_RESULT = {
    "response": "test response",
    "citations": {"personal": [], "knowledge": []},
    "confidence": "low",
}


def test_query_returns_429_when_rate_limited(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch(
        "services.rate_limit_service.check_and_increment",
        return_value=_MOCK_RATE_DENIED,
    ):
        response = client.post("/query", json={"query": "How do I squat?"})
    assert response.status_code == 429
    detail = response.json()["detail"]
    assert detail["code"] == "RATE_LIMIT_EXCEEDED"
    assert "resetAt" in detail["detail"]
    assert detail["detail"]["limit"] == 3


def test_analyze_returns_429_when_rate_limited(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch(
        "services.rate_limit_service.check_and_increment",
        return_value=_MOCK_RATE_DENIED,
    ):
        response = client.post("/analyze", json={"program": "Day 1: Squat 5x5"})
    assert response.status_code == 429
    detail = response.json()["detail"]
    assert detail["code"] == "RATE_LIMIT_EXCEEDED"
    assert "resetAt" in detail["detail"]
    assert detail["detail"]["limit"] == 3


def test_query_passes_user_context_to_rate_limiter(monkeypatch):
    client = _bypass_client(monkeypatch)
    mock_increment = MagicMock(return_value=_MOCK_RATE_ALLOWED)
    with patch("services.rate_limit_service.check_and_increment", mock_increment), \
         patch("services.rag_service.query", return_value=dict(_MOCK_RAG_RESULT)):
        response = client.post("/query", json={"query": "How do I bench press?"})

    assert response.status_code == 200
    mock_increment.assert_called_once()
    call_kwargs = mock_increment.call_args
    assert call_kwargs.args[0] == "test-user-001"
    assert call_kwargs.kwargs["user_create_date"] == "2025-01-01T00:00:00"
    assert call_kwargs.kwargs["is_premium"] is False
