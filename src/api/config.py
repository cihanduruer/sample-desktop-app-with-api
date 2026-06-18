"""Application configuration, sourced from environment variables.

Secrets and environment-specific settings live here (read from the environment),
not hard-coded in source. Defaults are chosen to be safe for local development.
"""
import os
from dataclasses import dataclass, field


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration for the API."""

    secret_key: str
    database_path: str
    host: str
    port: int
    debug: bool
    default_page_size: int
    max_page_size: int
    cors_origins: list[str] = field(default_factory=list)

    @staticmethod
    def from_env() -> "Config":
        return Config(
            secret_key=_env_str("ORDER_API_SECRET_KEY", "dev-only-insecure-key"),
            database_path=_env_str(
                "ORDER_API_DB_PATH", os.path.join(_BASE_DIR, "orders.db")
            ),
            # Secure default: bind to loopback only. Containers override with 0.0.0.0.
            host=_env_str("ORDER_API_HOST", "127.0.0.1"),
            port=_env_int("ORDER_API_PORT", 5001),
            debug=_env_bool("ORDER_API_DEBUG", False),
            default_page_size=_env_int("ORDER_API_PAGE_SIZE", 50),
            max_page_size=_env_int("ORDER_API_MAX_PAGE_SIZE", 200),
            cors_origins=_env_list(
                "ORDER_API_CORS_ORIGINS",
                ["http://localhost:5080", "http://localhost:5173"],
            ),
        )
