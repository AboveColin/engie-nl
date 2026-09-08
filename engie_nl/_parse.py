"""Turning a decoded response into models.

Both the client's own reads and the endpoint groups need these, and importing
one from the other would tie them together in a circle, so they live here.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")

Params = list[tuple[str, str]]


def eans_param(eans: Iterable[str] | str) -> Params:
    """``eans[]`` is one query key per value; a comma-joined string is rejected."""
    values = [eans] if isinstance(eans, str) else list(eans)
    if not values:
        raise ValueError("at least one EAN is required")
    return [("eans[]", ean) for ean in values]


def as_dicts(data: Any) -> list[dict[str, Any]]:
    """The list of objects in a response, whether it is bare or wrapped in ``data``."""
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [d for d in data["data"] if isinstance(d, dict)]
    return []


def parse_list(data: Any, model: Callable[[dict[str, Any]], T]) -> list[T]:
    """Every object in a list response, as models. A non-list gives an empty list."""
    return [model(d) for d in as_dicts(data)]


def parse_one(data: Any, model: Callable[[dict[str, Any]], T]) -> T | None:
    """One object response as a model, or None when the body was not an object."""
    return model(data) if isinstance(data, dict) else None
