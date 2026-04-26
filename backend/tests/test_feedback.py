"""Tests for POST /feedback endpoint."""
import os
from unittest.mock import patch

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
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)


def test_feedback_thumbs_up_returns_200(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.feedback_service.submit_feedback", return_value=None):
        response = client.post("/feedback", json={"queryId": "test-query-id", "rating": "up"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["queryId"] == "test-query-id"
    assert data["rating"] == "up"


def test_feedback_thumbs_down_returns_200(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.feedback_service.submit_feedback", return_value=None):
        response = client.post("/feedback", json={"queryId": "test-query-id", "rating": "down"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["queryId"] == "test-query-id"
    assert data["rating"] == "down"


def test_feedback_invalid_rating_returns_422(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.feedback_service.submit_feedback", return_value=None):
        response = client.post("/feedback", json={"queryId": "test-query-id", "rating": "neutral"})
    assert response.status_code == 422


def test_feedback_requires_auth():
    monkeypatch_dummy = None
    # No bypass — use real unauthenticated client
    import importlib
    import sys
    # Ensure we get a fresh unauthenticated client
    from fastapi.testclient import TestClient as TC
    # Re-import main without auth bypass
    if 'main' in sys.modules:
        del sys.modules['main']
    from main import app
    client = TC(app)
    response = client.post("/feedback", json={"queryId": "test-query-id", "rating": "up"})
    assert response.status_code == 401


def test_feedback_missing_query_id_returns_422(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.feedback_service.submit_feedback", return_value=None):
        response = client.post("/feedback", json={"rating": "up"})
    assert response.status_code == 422
