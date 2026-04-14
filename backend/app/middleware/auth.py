"""
JWT authentication middleware for FastAPI.

Validates Cognito-issued JWT access tokens by fetching the User Pool's
public JWKS and verifying the token signature and claims.
"""

import urllib.request
import json
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

# FastAPI security scheme — extracts Bearer token from Authorization header
bearer_scheme = HTTPBearer()

# Cache the JWKS (JSON Web Key Set) from Cognito to avoid repeated fetches
_JWKS_CACHE: dict | None = None


def _get_jwks() -> dict:
    """Fetch and cache the Cognito User Pool JWKS."""
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        jwks_url = (
            f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
            f"{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )
        with urllib.request.urlopen(jwks_url) as response:
            _JWKS_CACHE = json.loads(response.read())
    return _JWKS_CACHE


def verify_token(token: str) -> dict:
    """Verify a Cognito JWT access token and return its claims.

    Args:
        token: Raw JWT string from the Authorization header.

    Returns:
        Dict of JWT claims (includes 'username', 'sub', etc.).

    Raises:
        HTTPException 401: If the token is invalid, expired, or untrusted.
    """
    try:
        # Decode header to find the key id (kid)
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        # Find the matching public key in the JWKS
        jwks = _get_jwks()
        public_key = None
        for key_data in jwks["keys"]:
            if key_data["kid"] == kid:
                public_key = jwk.construct(key_data)
                break

        if public_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Public key not found in JWKS",
            )

        # Verify signature and decode claims
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID,
        )

        # Ensure this is an access token (not an id token)
        if claims.get("token_use") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not an access token",
            )

        return claims

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(exc)}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """FastAPI dependency that extracts and validates the current user.

    Inject into any protected route with:
        current_user: dict = Depends(get_current_user)

    Args:
        credentials: Bearer token extracted by FastAPI.

    Returns:
        Dict of JWT claims for the authenticated user.
    """
    return verify_token(credentials.credentials)
