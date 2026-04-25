"""
Exercise endpoint tests for Story 2.1.

All auth-passing tests use AUTH_BYPASS=true via monkeypatch.
"""
import config
import middleware.auth as auth_module
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    from main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /exercises — all sports (no filter)
# ---------------------------------------------------------------------------


def test_get_exercises_returns_all_sports(monkeypatch):
    """GET /exercises → 200 with all four sport keys."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises")
    assert response.status_code == 200
    body = response.json()
    exercises = body["data"]["exercises"]
    for sport in ("grip", "armwrestling", "powerlifting", "general"):
        assert sport in exercises, f"Missing sport key: {sport}"
        assert len(exercises[sport]) > 0, f"Empty exercise list for sport: {sport}"


# ---------------------------------------------------------------------------
# GET /exercises?sportType=grip
# ---------------------------------------------------------------------------


def test_get_exercises_filter_grip(monkeypatch):
    """GET /exercises?sportType=grip → 200 with only grip exercises."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises?sportType=grip")
    assert response.status_code == 200
    body = response.json()
    exercises = body["data"]["exercises"]
    assert list(exercises.keys()) == ["grip"], "Response should only have 'grip' key"
    names = [e["name"] for e in exercises["grip"]]
    for expected in ("Gripper Close", "Hub Lift", "Pinch Block", "Wrist Curl", "Fat Bar"):
        assert expected in names, f"Expected '{expected}' in grip exercises"


# ---------------------------------------------------------------------------
# GET /exercises?sportType=armwrestling
# ---------------------------------------------------------------------------


def test_get_exercises_filter_armwrestling(monkeypatch):
    """GET /exercises?sportType=armwrestling → 200 with only armwrestling exercises."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises?sportType=armwrestling")
    assert response.status_code == 200
    body = response.json()
    exercises = body["data"]["exercises"]
    assert list(exercises.keys()) == ["armwrestling"]
    names = [e["name"] for e in exercises["armwrestling"]]
    assert "Pronation" in names
    assert "Supination" in names


# ---------------------------------------------------------------------------
# GET /exercises?sportType=invalid → 400
# ---------------------------------------------------------------------------


def test_get_exercises_invalid_sport_type(monkeypatch):
    """GET /exercises?sportType=invalid → 400 VALIDATION_ERROR."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises?sportType=invalid")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "VALIDATION_ERROR"
    assert "validValues" in detail["detail"]


# ---------------------------------------------------------------------------
# GET /exercises — no auth → 401
# ---------------------------------------------------------------------------


def test_get_exercises_requires_auth(monkeypatch):
    """GET /exercises without auth token → 401 when AUTH_BYPASS is false."""
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    monkeypatch.setattr(config, "AUTH_BYPASS", "false")
    from main import app
    client = TestClient(app)
    response = client.get("/exercises")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# camelCase field assertion
# ---------------------------------------------------------------------------


def test_exercise_response_uses_camel_case(monkeypatch):
    """Exercise objects in response use sportType (camelCase), not sport_type."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises?sportType=grip")
    assert response.status_code == 200
    first_exercise = response.json()["data"]["exercises"]["grip"][0]
    assert "sportType" in first_exercise, "'sportType' key missing — camelCase not enforced"
    assert "sport_type" not in first_exercise, "'sport_type' key present — snake_case leaked into response"


# ---------------------------------------------------------------------------
# All sports have non-empty exercise lists
# ---------------------------------------------------------------------------


def test_all_sports_non_empty(monkeypatch):
    """Each sport's exercise list is non-empty."""
    client = _bypass_client(monkeypatch)
    response = client.get("/exercises")
    assert response.status_code == 200
    exercises = response.json()["data"]["exercises"]
    for sport in ("grip", "armwrestling", "powerlifting", "general"):
        assert len(exercises[sport]) > 0, f"{sport} exercise list is empty"
