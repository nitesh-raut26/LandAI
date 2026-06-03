"""Google OAuth — real, env-gated. Two supported flows:

1. **Google Identity Services (primary, SPA-friendly)** — the frontend renders the
   Google button, gets an ID-token *credential*, and POSTs it to ``/api/auth/google``.
   :func:`verify_id_token` validates the token against Google's public JWKS
   (RS256, ``aud`` = our client id, ``iss`` = accounts.google.com).
2. **Authorization-code redirect** — :func:`authorization_url` builds the consent
   URL and :func:`exchange_code` swaps the returned ``code`` for an ID token at the
   token endpoint. Useful for non-SPA clients.

Everything activates only when ``GOOGLE_CLIENT_ID`` (+ ``GOOGLE_CLIENT_SECRET`` for
the code flow) are set; otherwise :func:`enabled` is False and the routes return a
clear "not configured" response instead of pretending. No secrets are committed —
this is dark until you supply a Google OAuth app's credentials.
"""
from __future__ import annotations

import os
import time
from typing import Any
from urllib.parse import urlencode

_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}

_jwks_cache: dict[str, Any] = {"keys": None, "at": 0.0}


def client_id() -> str | None:
    return os.getenv("GOOGLE_CLIENT_ID")


def client_secret() -> str | None:
    return os.getenv("GOOGLE_CLIENT_SECRET")


def redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")


def enabled() -> bool:
    """Identity-Services (ID-token) flow needs only the client id."""
    return bool(client_id())


def code_flow_enabled() -> bool:
    """The redirect/auth-code flow additionally needs the client secret."""
    return bool(client_id() and client_secret())


def authorization_url(state: str) -> str:
    params = {
        "client_id": client_id() or "",
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{_AUTH_URL}?{urlencode(params)}"


def _jwks() -> dict[str, Any]:
    now = time.time()
    if _jwks_cache["keys"] and now - _jwks_cache["at"] < 3600:
        return _jwks_cache["keys"]
    import httpx

    resp = httpx.get(_CERTS_URL, timeout=8.0)
    resp.raise_for_status()
    keys = resp.json()
    _jwks_cache.update(keys=keys, at=now)
    return keys


def verify_id_token(token: str) -> dict[str, Any] | None:
    """Validate a Google ID token and return its claims, or None if invalid.

    Checks RS256 signature against Google's JWKS, ``aud`` == our client id, and
    ``iss`` is a Google issuer. Returns claims incl. ``email``, ``sub``, ``name``.
    """
    cid = client_id()
    if not cid or not token:
        return None
    try:
        from jose import jwt

        claims = jwt.decode(
            token, _jwks(), algorithms=["RS256"], audience=cid,
            options={"verify_at_hash": False},
        )
    except Exception:
        return None
    if claims.get("iss") not in _ISSUERS:
        return None
    if not claims.get("email"):
        return None
    return claims


def exchange_code(code: str) -> dict[str, Any] | None:
    """Exchange an authorization code for tokens; returns the verified ID-token
    claims (or None). Requires the client secret (code-flow)."""
    if not code_flow_enabled() or not code:
        return None
    try:
        import httpx

        resp = httpx.post(_TOKEN_URL, data={
            "code": code,
            "client_id": client_id(),
            "client_secret": client_secret(),
            "redirect_uri": redirect_uri(),
            "grant_type": "authorization_code",
        }, timeout=8.0)
        if resp.status_code != 200:
            return None
        id_token = resp.json().get("id_token")
    except Exception:
        return None
    return verify_id_token(id_token) if id_token else None
