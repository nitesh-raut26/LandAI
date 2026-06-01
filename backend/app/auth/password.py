"""
Password hashing.

Default scheme is ``pbkdf2_sha256`` (pure-Python, no native build, zero install
friction, and a sound KDF used by Django). ``bcrypt`` / ``argon2`` are drop-in via
``PASSWORD_SCHEME`` + the matching passlib extra. We never store plaintext.
"""
from __future__ import annotations

import os

from passlib.context import CryptContext

_SCHEME = os.getenv("PASSWORD_SCHEME", "pbkdf2_sha256")
_ctx = CryptContext(schemes=[_SCHEME], deprecated="auto")


def hash_password(plain: str) -> str:
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ctx.verify(plain, hashed)
    except Exception:
        return False
