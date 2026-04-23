"""Clerk JWT authentication middleware for protected endpoints."""

import os
import time
import requests
import jwt
from jwt import algorithms as jwt_algorithms
from typing import Optional
from dataclasses import dataclass
from fastapi import HTTPException, Request, status


CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "")

# JWKS cache (in-memory, 1-hour TTL)
_jwks_cache: Optional[dict] = None
_jwks_cache_time: float = 0.0
JWKS_CACHE_TTL: int = 3600  # 1 hour


async def get_cached_jwks() -> dict:
    """Fetch and cache Clerk JWKS public keys.

    Returns:
        JWKS dict with 'keys' list.

    Raises:
        HTTPException: If JWKS fetch fails.
    """
    global _jwks_cache, _jwks_cache_time

    if _jwks_cache is not None and (time.time() - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache

    try:
        response = requests.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = time.time()
        return _jwks_cache
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro ao buscar chaves de autenticação: {str(e)}",
        )


@dataclass
class ClerkAuthState:
    """Authenticated user state from Clerk JWT."""
    clerk_id: str
    email: Optional[str] = None
    payload: Optional[dict] = None


async def verify_clerk_token(token: str) -> ClerkAuthState:
    """Verify a Clerk JWT token using JWKS.

    Args:
        token: JWT token string.

    Returns:
        ClerkAuthState with verified claims.

    Raises:
        HTTPException: On invalid/expired/malformed tokens.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        jwks = await get_cached_jwks()

        public_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key = jwt_algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"X-Error-Code": "INVALID_KEY"},
            )

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={
                "verify_exp": True,
                "verify_iss": True,
                "verify_signature": True,
            },
        )

        clerk_id = payload.get("sub")
        if not clerk_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sem identificador de usuário",
                headers={"X-Error-Code": "NO_SUB"},
            )

        return ClerkAuthState(
            clerk_id=clerk_id,
            email=payload.get("email"),
            payload=payload,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"X-Error-Code": "TOKEN_EXPIRED"},
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token mal formatado",
            headers={"X-Error-Code": "TOKEN_MALFORMED"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"X-Error-Code": "TOKEN_INVALID"},
        )


async def require_clerk_auth(request: Request) -> ClerkAuthState:
    """FastAPI dependency that requires valid Clerk JWT.

    Raises:
        HTTPException 401: Missing/invalid Authorization header.
        HTTPException 503: Auth service not configured.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization requerido",
            headers={"X-Error-Code": "MISSING_AUTH_HEADER"},
        )

    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato Authorization deve ser 'Bearer <token>'",
            headers={"X-Error-Code": "INVALID_AUTH_FORMAT"},
        )

    token = auth_header[7:]  # strip "Bearer "
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token vazio",
            headers={"X-Error-Code": "EMPTY_TOKEN"},
        )

    if not CLERK_JWKS_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação não configurado",
            headers={"X-Error-Code": "AUTH_NOT_CONFIGURED"},
        )

    return await verify_clerk_token(token)


async def get_optional_clerk_auth(request: Request) -> Optional[ClerkAuthState]:
    """FastAPI dependency for optional auth — returns None if no token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    if not auth_header.lower().startswith("bearer "):
        return None

    token = auth_header[7:]
    if not token:
        return None

    if not CLERK_JWKS_URL:
        return None

    try:
        return await verify_clerk_token(token)
    except HTTPException:
        return None
