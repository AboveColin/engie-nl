"""Session ownership and body decoding, the two rules both clients share."""

from __future__ import annotations

import aiohttp
import pytest
from aiohttp import web

from engie_nl._http import SessionOwner, json_or_text, send
from engie_nl.exceptions import EngieNetworkError

from tests.conftest import FakeServer


async def test_a_created_session_is_closed_and_a_borrowed_one_is_not() -> None:
    """Home Assistant passes its own session; closing it would break the rest of HA."""
    borrowed = aiohttp.ClientSession()
    owner = SessionOwner(borrowed, timeout=5)
    assert await owner._get_session() is borrowed  # pylint: disable=protected-access
    await owner.close()
    assert not borrowed.closed
    await borrowed.close()

    mine = SessionOwner(None, timeout=5)
    created = await mine._get_session()  # pylint: disable=protected-access
    await mine.close()
    assert created.closed


async def test_a_closed_borrowed_session_is_replaced() -> None:
    """A caller may hand over a session and close it later; the next request still works."""
    borrowed = aiohttp.ClientSession()
    owner = SessionOwner(borrowed, timeout=5)
    await borrowed.close()
    replacement = await owner._get_session()  # pylint: disable=protected-access
    assert replacement is not borrowed and not replacement.closed
    await owner.close()
    assert replacement.closed


async def test_session_owner_is_its_own_context_manager() -> None:
    async with SessionOwner(None, timeout=5) as owner:
        created = await owner._get_session()  # pylint: disable=protected-access
    assert created.closed


async def test_json_or_text_reads_the_three_body_shapes(server: FakeServer) -> None:
    """An empty body is {}, JSON is decoded whatever the content type, the rest is text."""
    server.handle("GET", "/empty", lambda _r: web.Response(status=204))
    server.handle("GET", "/text", lambda _r: web.Response(text="Service Unavailable"))
    # The gateway sends JSON as text/plain on at least one path, so the decode
    # must not depend on the content type.
    server.handle("GET", "/mislabelled", lambda _r: web.Response(text='{"ok": true}', content_type="text/plain"))

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server.url}/empty") as resp:
            assert await json_or_text(resp) == {}
        async with session.get(f"{server.url}/text") as resp:
            assert await json_or_text(resp) == "Service Unavailable"
        async with session.get(f"{server.url}/mislabelled") as resp:
            assert await json_or_text(resp) == {"ok": True}


async def test_send_turns_a_transport_failure_into_one_type() -> None:
    """Callers retry on EngieNetworkError, so every transport failure has to become one."""
    async with aiohttp.ClientSession() as session:
        with pytest.raises(EngieNetworkError) as err:
            # Port 1 on loopback refuses, which aiohttp raises as a ClientError.
            await send(session, "GET", "http://127.0.0.1:1/nothing")
    assert "GET http://127.0.0.1:1/nothing failed" in str(err.value)


async def test_send_returns_the_status_rather_than_raising(server: FakeServer) -> None:
    """What a 4xx means differs per host, so send() hands it back undecided."""
    server.json("/gone", {"message": "no"}, status=404)
    async with aiohttp.ClientSession() as session:
        assert await send(session, "GET", f"{server.url}/gone") == (404, {"message": "no"})
