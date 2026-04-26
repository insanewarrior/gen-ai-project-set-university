"""Tests for GET /profile endpoint."""
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
    monkeypatch.setattr(config, "TEST_USER_CREATE_DATE", "2025-01-01T00:00:00")
    monkeypatch.setattr(config, "TEST_IS_PREMIUM", "false")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)


def test_profile_returns_200_with_stats(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.profile_service.get_total_session_count", return_value=5), \
         patch("services.profile_service.get_total_query_count", return_value=12), \
         patch("services.rate_limit_service.get_today_count", return_value=1):
        response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "totalSessions" in data
    assert "totalQueries" in data
    assert "tier" in data
    assert "accountCreatedAt" in data
    assert "queriesRemainingToday" in data
    assert "tierLimit" in data
    assert data["totalSessions"] == 5
    assert data["totalQueries"] == 12


def test_profile_free_tier_queries_remaining(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.profile_service.get_total_session_count", return_value=0), \
         patch("services.profile_service.get_total_query_count", return_value=1), \
         patch("services.rate_limit_service.get_today_count", return_value=1):
        response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["queriesRemainingToday"] == 2
    assert data["tierLimit"] == 3
    assert data["tier"] == "free"


def test_profile_exhausted_queries(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.profile_service.get_total_session_count", return_value=0), \
         patch("services.profile_service.get_total_query_count", return_value=3), \
         patch("services.rate_limit_service.get_today_count", return_value=3):
        response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["queriesRemainingToday"] == 0
    assert data["tierLimit"] == 3


def test_profile_premium_queries_remaining_is_minus_one(monkeypatch):
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    monkeypatch.setattr(config, "TEST_USER_CREATE_DATE", "2025-01-01T00:00:00")
    monkeypatch.setattr(config, "TEST_IS_PREMIUM", "true")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    client = TestClient(app)
    with patch("services.profile_service.get_total_session_count", return_value=10), \
         patch("services.profile_service.get_total_query_count", return_value=50), \
         patch("services.rate_limit_service.get_today_count", return_value=5):
        response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["queriesRemainingToday"] == -1
    assert data["tierLimit"] == -1
    assert data["tier"] == "premium"


def test_profile_requires_auth(monkeypatch):
    monkeypatch.setattr(config, "AUTH_BYPASS", "false")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/profile")
    assert response.status_code == 401
