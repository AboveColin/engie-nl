"""Shared fixtures: a loopback Okta and a loopback gateway.

The client and the auth module take their base URLs as arguments, so the tests
run them against a real aiohttp server on 127.0.0.1 rather than mocking
aiohttp. That exercises status codes, redirects and connection failures for
real, and it does not break when aiohttp bumps a version.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any
from urllib.parse import parse_qs, urlencode

import pytest
import pytest_asyncio
from aiohttp import web

from engie_nl import EngieClient, OktaAuth, TokenSet

USERNAME = "klant@example.com"
PASSWORD = "geheim"
SESSION_TOKEN = "sess-1"
CODE = "code-1"
ACCESS = "okta-access-1"
REFRESH = "okta-refresh-1"
CLIENT_ID = "0oatest"
REDIRECT = "engie://login/okta/callback"

Handler = Callable[[web.Request], Any]


class FakeServer:
    """One loopback aiohttp app whose routes a test fills in."""

    def __init__(self) -> None:
        self.app = web.Application()
        self.requests: list[web.Request] = []
        self.forms: list[dict[str, str]] = []
        self.jsons: list[Any] = []
        self._routes: dict[tuple[str, str], Handler] = {}
        self.app.router.add_route("*", "/{tail:.*}", self._dispatch)
        self.url = ""

    def handle(self, method: str, path: str, handler: Handler) -> None:
        self._routes[(method, path)] = handler

    def json(self, path: str, payload: Any, status: int = 200, method: str = "GET") -> None:
        self.handle(method, path, lambda _r: web.json_response(payload, status=status))

    def sequence(self, path: str, *responses: tuple[int, Any], method: str = "GET") -> None:
        remaining = list(responses)

        def _next(_r: web.Request) -> web.Response:
            status, payload = remaining.pop(0) if len(remaining) > 1 else remaining[0]
            return web.json_response(payload, status=status)

        self.handle(method, path, _next)

    async def _dispatch(self, request: web.Request) -> web.StreamResponse:
        self.requests.append(request)
        if request.can_read_body:
            if request.content_type == "application/json":
                self.jsons.append(await request.json())
            else:
                self.forms.append({k: v for k, v in (await request.post()).items() if isinstance(v, str)})
        handler = self._routes.get((request.method, request.path))
        if handler is None:
            return web.json_response({"error": "no route", "path": request.path}, status=404)
        result = handler(request)
        if hasattr(result, "__await__"):
            result = await result
        return result  # type: ignore[no-any-return]


@pytest_asyncio.fixture
async def server() -> AsyncIterator[FakeServer]:
    fake = FakeServer()
    runner = web.AppRunner(fake.app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    fake.url = f"http://127.0.0.1:{port}"
    try:
        yield fake
    finally:
        await runner.cleanup()


@pytest.fixture
def okta_ok(server: FakeServer) -> FakeServer:
    """An Okta that accepts USERNAME/PASSWORD and hands out ACCESS/REFRESH."""

    def authn(request: web.Request) -> web.Response:
        body = server.jsons[-1]
        if body.get("username") == USERNAME and body.get("password") == PASSWORD:
            return web.json_response({"status": "SUCCESS", "sessionToken": SESSION_TOKEN})
        return web.json_response(
            {"errorCode": "E0000004", "errorSummary": "Authentication failed"}, status=401
        )

    def authorize(request: web.Request) -> web.Response:
        q = request.query
        assert q["client_id"] == CLIENT_ID
        assert q["code_challenge_method"] == "S256"
        assert q["response_type"] == "code"
        if q.get("sessionToken") != SESSION_TOKEN:
            loc = f"{REDIRECT}?{urlencode({'error': 'login_required', 'state': q['state']})}"
        else:
            loc = f"{REDIRECT}?{urlencode({'code': CODE, 'state': q['state']})}"
        return web.Response(status=302, headers={"Location": loc})

    def token(request: web.Request) -> web.Response:
        form = server.forms[-1]
        grant = form.get("grant_type")
        if grant == "authorization_code" and form.get("code") == CODE and form.get("code_verifier"):
            return web.json_response(_tokens(ACCESS, REFRESH))
        if grant == "refresh_token" and form.get("refresh_token") == REFRESH:
            return web.json_response(_tokens("okta-access-2", "okta-refresh-2"))
        if grant == "password":
            return web.json_response(
                {"error": "unsupported_grant_type", "error_description": "not enabled"}, status=400
            )
        return web.json_response({"error": "invalid_grant"}, status=400)

    server.handle("POST", "/api/v1/authn", authn)
    server.handle("GET", "/oauth2/default/v1/authorize", authorize)
    server.handle("POST", "/oauth2/default/v1/token", token)
    return server


def _tokens(access: str, refresh: str) -> dict[str, Any]:
    return {
        "token_type": "Bearer",
        "expires_in": 3600,
        "access_token": access,
        "refresh_token": refresh,
        "scope": "openid email profile offline_access",
        "id_token": "id.token.x",
    }


@pytest.fixture
def auth(server: FakeServer) -> OktaAuth:
    return OktaAuth(
        client_id=CLIENT_ID,
        issuer=f"{server.url}/oauth2/default",
        org_url=server.url,
        redirect_uri=REDIRECT,
        timeout=5,
    )


@pytest.fixture
def tokens() -> TokenSet:
    return TokenSet(access_token=ACCESS, refresh_token=REFRESH, expires_at=9_999_999_999.0)


@pytest_asyncio.fixture
async def client(server: FakeServer, auth: OktaAuth, tokens: TokenSet) -> AsyncIterator[EngieClient]:
    async with EngieClient(tokens, auth=auth, base_url=server.url, timeout=5) as c:
        yield c
    await auth.close()


def query_of(request: web.Request) -> dict[str, list[str]]:
    return parse_qs(request.query_string, keep_blank_values=True)
