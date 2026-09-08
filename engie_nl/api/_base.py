"""Shared plumbing for the endpoint groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._parse import Params, as_dicts, eans_param, parse_list, parse_one

if TYPE_CHECKING:  # pragma: no cover - the import is a cycle at runtime
    from ..client import EngieClient

__all__ = ["ApiGroup", "Params", "as_dicts", "eans_param", "parse_list", "parse_one"]


class ApiGroup:  # pylint: disable=too-few-public-methods
    """One area of the gateway, bound to the client that owns the session."""

    def __init__(self, client: "EngieClient") -> None:
        self._client = client

    async def _get(self, path: str, params: Params | None = None) -> Any:
        return await self._client._get(path, params)  # pylint: disable=protected-access

    async def _query(self, verb: str, path: str, **kwargs: Any) -> Any:
        """A request that reads despite not being a GET, so no write gate."""
        return await self._client._request(verb, path, **kwargs)  # pylint: disable=protected-access

    async def _write(self, verb: str, path: str, **kwargs: Any) -> Any:
        return await self._client._write(verb, path, **kwargs)  # pylint: disable=protected-access
