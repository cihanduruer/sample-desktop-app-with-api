"""Password hashing and token generation.

Passwords are hashed with a vetted algorithm (PBKDF2 via Werkzeug); plaintext is
never stored or logged. Tokens are random and opaque.
"""
import secrets

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(plaintext: str) -> str:
    """Return a salted hash suitable for storage."""
    return generate_password_hash(plaintext)


def verify_password(password_hash: str, plaintext: str) -> bool:
    """Return True when ``plaintext`` matches the stored hash."""
    return check_password_hash(password_hash, plaintext)


def generate_token() -> str:
    """Return a cryptographically random, URL-safe opaque token."""
    return secrets.token_urlsafe(32)
