from typing import Optional

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

import config

security = HTTPBearer(auto_error=False)

_jwks_cache: Optional[dict] = None  # module-level cache per Lambda instance


def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        region = config.COGNITO_REGION
        pool_id = config.COGNITO_USER_POOL_ID
        url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    # AUTH_BYPASS mode for local development
    if config.AUTH_BYPASS.lower() == "true":
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
            options={"verify_aud": False},  # Cognito uses client_id in aud, skip strict check
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


# Type alias for cleaner router signatures
CurrentUser = str
