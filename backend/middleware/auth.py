from datetime import datetime, timedelta
from typing import Optional, TypedDict

import boto3
import httpx
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

import config

security = HTTPBearer(auto_error=False)

_jwks_cache: Optional[dict] = None  # module-level cache per Lambda instance


class UserContext(TypedDict):
    user_id: str
    user_create_date: str | None  # ISO 8601 from Cognito, None if unavailable
    is_premium: bool


def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        region = config.COGNITO_REGION
        pool_id = config.COGNITO_USER_POOL_ID
        url = (
            f"https://cognito-idp.{region}.amazonaws.com"
            f"/{pool_id}/.well-known/jwks.json"
        )
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def _get_user_create_date(user_id: str) -> str | None:
    try:
        client = boto3.client("cognito-idp", region_name=config.COGNITO_REGION)
        response = client.admin_get_user(
            UserPoolId=config.COGNITO_USER_POOL_ID,
            Username=user_id,
        )
        create_date = response.get("UserCreateDate")
        if create_date:
            return create_date.isoformat()
        return None
    except Exception:
        return None  # Fail open: treat as free tier


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    # AUTH_BYPASS mode for local development
    if config.AUTH_BYPASS.lower() == "true":
        dev_user = request.headers.get("x-dev-user", "").lower()
        if dev_user in _DEV_USERS:
            return _DEV_USERS[dev_user]()["user_id"]
        return config.TEST_USER_ID

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "code": "MISSING_TOKEN"},
        )

    token = credentials.credentials
    try:
        jwks = _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Cognito client_id in aud
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail={"error": "Unauthorized", "code": "INVALID_TOKEN"},
            )
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Token expired", "code": "TOKEN_EXPIRED"},
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "code": "INVALID_TOKEN"},
        )


_DEV_USERS = {
    "free": lambda: UserContext(
        user_id="test-user-free",
        user_create_date="2025-01-01T00:00:00",
        is_premium=False,
    ),
    "onboarding": lambda: UserContext(
        user_id="test-user-onboarding",
        user_create_date=(datetime.utcnow() - timedelta(days=2)).isoformat(),
        is_premium=False,
    ),
    "premium": lambda: UserContext(
        user_id="test-user-premium",
        user_create_date="2025-01-01T00:00:00",
        is_premium=True,
    ),
}


async def get_user_context(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> UserContext:
    # AUTH_BYPASS mode for local development
    if config.AUTH_BYPASS.lower() == "true":
        dev_user = request.headers.get("x-dev-user", "").lower()
        if dev_user in _DEV_USERS:
            return _DEV_USERS[dev_user]()
        return UserContext(
            user_id=config.TEST_USER_ID,
            user_create_date=config.TEST_USER_CREATE_DATE,
            is_premium=config.TEST_IS_PREMIUM.lower() == "true",
        )

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "code": "MISSING_TOKEN"},
        )

    token = credentials.credentials
    try:
        jwks = _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail={"error": "Unauthorized", "code": "INVALID_TOKEN"},
            )

        groups: list[str] = payload.get("cognito:groups", []) or []
        is_premium = "premium" in groups

        user_create_date = _get_user_create_date(user_id)

        return UserContext(
            user_id=user_id,
            user_create_date=user_create_date,
            is_premium=is_premium,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Token expired", "code": "TOKEN_EXPIRED"},
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "code": "INVALID_TOKEN"},
        )


# Type alias for cleaner router signatures
CurrentUser = str
