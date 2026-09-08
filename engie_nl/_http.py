"""Shared aiohttp session handling for the auth and gateway clients.

Home Assistant passes its own session; scripts pass none and get one that is
closed with the owner. Both classes need that same rule, so it lives once.
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .exceptions import EngieNetworkError


class SessionOwner:
    """Holds an aiohttp session, creating one lazily and closing only what it created."""

    def __init__(self, session: aiohttp.ClientSession | None, timeout: float) -> None:
        self._session: aiohttp.ClientSession | None = session
        self._owns_session: bool = session is None
        self._timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=timeout)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
            self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Close the session if this object created it. A borrowed session is left alone."""
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "SessionOwner":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()


async def json_or_text(resp: aiohttp.ClientResponse) -> Any:
    """Decode a response as JSON when it is, otherwise return the text; empty body -> ``{}``."""
    text = await resp.text()
    if not text:
        return {}
    try:
        return await resp.json(content_type=None)
    except (aiohttp.ContentTypeError, ValueError):
        return text


async def send(
    session: aiohttp.ClientSession,
    verb: str,
    url: str,
    *,
    params: list[tuple[str, str]] | None = None,
    form: list[tuple[str, str]] | None = None,
    json_body: Any = None,
    headers: dict[str, str] | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
) -> tuple[int, Any]:
    """One request, returning ``(status, body)``.

    Both the gateway client and the Net2Grid client need exactly this, down to
    turning every transport failure into :class:`EngieNetworkError` so callers
    can retry on one type. The status is returned rather than raised on, because
    what a 4xx means differs per host.
    """
    try:
        async with session.request(
            verb,
            url,
            params=params,
            data=form,
            json=json_body,
            headers=headers,
            timeout=timeout,
        ) as resp:
            return resp.status, await json_or_text(resp)
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise EngieNetworkError(f"{verb} {url} failed: {err or type(err).__name__}") from err
