"""Shared aiohttp session handling for the auth and gateway clients.

Home Assistant passes its own session; scripts pass none and get one that is
closed with the owner. Both classes need that same rule, so it lives once.
"""

from __future__ import annotations

from typing import Any

import aiohttp


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
