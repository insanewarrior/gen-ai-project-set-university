"""Tests for POST /export endpoint."""
import csv
import io
import os
from decimal import Decimal
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


_ONE_SESSION = [
    {
        "sessionDate": "2026-04-15",
        "sport": "grip",
        "notes": "felt strong",
        "exercises": [
            {
                "exerciseName": "Gripper Close",
                "sets": [
                    {"setNumber": Decimal("1"), "weight": Decimal("80"), "reps": Decimal("3"), "rpe": Decimal("9")},
                    {"setNumber": Decimal("2"), "weight": Decimal("80"), "reps": Decimal("3"), "rpe": Decimal("8.5")},
                ],
            }
        ],
    }
]


def test_export_returns_csv_content_type(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.session_service.get_sessions", return_value=[]):
        response = client.post("/export")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")


def test_export_empty_sessions_returns_headers_only(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.session_service.get_sessions", return_value=[]):
        response = client.post("/export")
    assert response.status_code == 200
    assert response.text == "date,sport,exercise,set,weight,reps,rpe,notes\r\n"


def test_export_with_sessions_returns_set_rows(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.session_service.get_sessions", return_value=_ONE_SESSION):
        response = client.post("/export")
    assert response.status_code == 200
    rows = list(csv.reader(io.StringIO(response.text)))
    assert len(rows) == 3  # header + 2 set rows
    assert rows[0] == ["date", "sport", "exercise", "set", "weight", "reps", "rpe", "notes"]
    assert rows[1] == ["2026-04-15", "grip", "Gripper Close", "1", "80", "3", "9", "felt strong"]
    assert rows[2] == ["2026-04-15", "grip", "Gripper Close", "2", "80", "3", "8.5", ""]


def test_export_requires_auth():
    import sys
    if "main" in sys.modules:
        del sys.modules["main"]
    from main import app
    from fastapi.testclient import TestClient as TC
    client = TC(app)
    response = client.post("/export")
    assert response.status_code == 401


def test_export_content_disposition(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.session_service.get_sessions", return_value=[]):
        response = client.post("/export")
    assert "training-data.csv" in response.headers["content-disposition"]
