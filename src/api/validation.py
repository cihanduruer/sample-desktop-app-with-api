"""Input validation and the API error type used to map failures to HTTP codes.

Validators raise :class:`ApiError` with an appropriate status code; the app's error
handler turns that into a JSON response. This keeps route handlers small and free of
nested ``if``/``try`` noise.
"""
import re
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_ORDER_STATUSES: tuple[str, ...] = (
    "NEW",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
)


class ApiError(Exception):
    """An error that maps to a specific HTTP status code and JSON message."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def require_json_object(payload: Any) -> dict:
    if not isinstance(payload, dict):
        raise ApiError("request body must be a JSON object", 400)
    return payload


def require_string(data: dict, field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"'{field}' is required", 400)
    return value.strip()


def require_email(data: dict, field: str = "email") -> str:
    value = require_string(data, field)
    if not EMAIL_PATTERN.match(value):
        raise ApiError(f"'{field}' is not a valid email address", 400)
    return value


def require_int(data: dict, field: str, minimum: int | None = None) -> int:
    value = data.get(field)
    # bool is a subclass of int; reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ApiError(f"'{field}' must be an integer", 400)
    if minimum is not None and value < minimum:
        raise ApiError(f"'{field}' must be >= {minimum}", 400)
    return value


def require_number(data: dict, field: str, minimum: float | None = None) -> float:
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ApiError(f"'{field}' must be a number", 400)
    if minimum is not None and value < minimum:
        raise ApiError(f"'{field}' must be >= {minimum}", 400)
    return float(value)


def require_status(value: str) -> str:
    if value not in VALID_ORDER_STATUSES:
        allowed = ", ".join(VALID_ORDER_STATUSES)
        raise ApiError(f"'status' must be one of: {allowed}", 400)
    return value


def validate_order_items(raw_items: Any) -> list[dict]:
    if not isinstance(raw_items, list) or not raw_items:
        raise ApiError("'items' must be a non-empty list", 400)

    validated: list[dict] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise ApiError(f"items[{index}] must be an object", 400)
        validated.append(
            {
                "product_id": require_int(item, "product_id", minimum=1),
                "quantity": require_int(item, "quantity", minimum=1),
            }
        )
    return validated


def parse_pagination(
    args: dict, default_page_size: int, max_page_size: int
) -> tuple[int, int, int]:
    """Return ``(page, page_size, offset)`` from query-string arguments."""
    page = _parse_positive_int(args.get("page"), default=1, name="page")
    page_size = _parse_positive_int(
        args.get("page_size"), default=default_page_size, name="page_size"
    )
    page_size = min(page_size, max_page_size)
    offset = (page - 1) * page_size
    return page, page_size, offset


def _parse_positive_int(raw: Any, default: int, name: str) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ApiError(f"'{name}' must be a positive integer", 400)
    if value < 1:
        raise ApiError(f"'{name}' must be a positive integer", 400)
    return value
