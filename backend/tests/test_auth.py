"""
Auth middleware tests for Story 1.3.

Integration tests use AUTH_BYPASS=true (no real Cognito needed).
Production-mode tests patch config.AUTH_BYPASS and middleware._get_jwks.
"""
import middleware.auth as auth_module
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# /health — must be public (no auth required)
# ---------------------------------------------------------------------------


def test_health_returns_200_without_auth(client):
    """GET /health should return 200 regardless of auth state."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /me — AUTH_BYPASS=false (production mode)
# ---------------------------------------------------------------------------


def test_me_returns_401_when_no_token(monkeypatch):
    """GET /me without Authorization header → 401 MISSING_TOKEN."""
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    import config
    monkeypatch.setattr(config, "AUTH_BYPASS", "false")

    from main import app
    response = TestClient(app).get("/me")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "MISSING_TOKEN"


def test_me_returns_401_with_invalid_token(monkeypatch):
    """GET /me with a malformed JWT → 401 INVALID_TOKEN."""
    import config
    monkeypatch.setattr(config, "AUTH_BYPASS", "false")
    # Provide empty JWKS so jwt.decode raises JWTError
    monkeypatch.setattr(auth_module, "_get_jwks", lambda: {"keys": []})

    from main import app
    response = TestClient(app).get(
        "/me", headers={"Authorization": "Bearer not.a.valid.jwt"}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] in ("INVALID_TOKEN", "TOKEN_EXPIRED")


# ---------------------------------------------------------------------------
# /me — AUTH_BYPASS=true (local development mode)
# ---------------------------------------------------------------------------


def test_me_returns_200_with_auth_bypass(monkeypatch):
    """GET /me with AUTH_BYPASS=true → 200 with TEST_USER_ID."""
    import config
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")

    from main import app
    response = TestClient(app).get("/me")
    assert response.status_code == 200
    assert response.json() == {"userId": "test-user-001"}


def test_me_no_token_succeeds_when_bypass_true(monkeypatch):
    """AUTH_BYPASS=true allows /me without any Authorization header."""
    import config
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")

    from main import app
    response = TestClient(app).get("/me")
    assert response.status_code == 200
