"""Shared fixtures: a loopback Okta and a loopback gateway.

The client and the auth module take their base URLs as arguments, so the tests
run them against a real aiohttp server on 127.0.0.1 rather than mocking
aiohttp. That exercises status codes, redirects and connection failures for
real, and it does not break when aiohttp bumps a version.

The fake Okta answers the Identity Engine flow the real org runs: interact,
introspect, identify, challenge/answer, token. Every remediation carries an
href back to this same server, because the client follows those hrefs rather
than assembling URLs of its own.
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
CODE = "code-1"
ACCESS = "okta-access-1"
REFRESH = "okta-refresh-1"
CLIENT_ID = "0oatest"
REDIRECT = "engie://login/okta/callback"

INTERACTION_HANDLE = "ih-1"
STATE_HANDLE = "sh-1"
INTERACTION_CODE = "ic-1"
PASSWORD_AUTHENTICATOR_ID = "autpassword1"
EMAIL_AUTHENTICATOR_ID = "autemail1"
EMAIL_CODE = "123456"

Handler = Callable[[web.Request], Any]


class FakeServer:
    """One loopback aiohttp app whose routes a test fills in."""

    def __init__(self) -> None:
        self.app = web.Application()
        self.requests: list[web.Request] = []
        self.forms: list[dict[str, str]] = []
        # The same forms with the repeats kept, because ``eans[]`` is one key
        # per value and a flat dict would show only the last one.
        self.multi_forms: list[dict[str, list[str]]] = []
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

    @property
    def paths(self) -> list[str]:
        """Path of every request the server saw, in order."""
        return [r.path for r in self.requests]

    async def _dispatch(self, request: web.Request) -> web.StreamResponse:
        self.requests.append(request)
        if request.can_read_body:
            # IDX bodies are application/ion+json, so match on "json", not equality.
            if "json" in (request.content_type or ""):
                self.jsons.append(await request.json())
            else:
                posted = await request.post()
                self.forms.append({k: v for k, v in posted.items() if isinstance(v, str)})
                self.multi_forms.append(
                    {k: [v for v in posted.getall(k) if isinstance(v, str)] for k in posted}
                )
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


# --- IDX response builders ---------------------------------------------------


def remediation(name: str, base: str, path: str, fields: list[dict[str, Any]]) -> dict[str, Any]:
    """One remediation, shaped as Okta sends it."""
    return {
        "rel": ["create-form"],
        "name": name,
        "href": f"{base}{path}",
        "method": "POST",
        "value": [*fields, {"name": "stateHandle", "required": True, "value": STATE_HANDLE}],
    }


def authenticator_option(label: str, method_type: str, identifier: str) -> dict[str, Any]:
    return {
        "label": label,
        "value": {
            "form": {
                "value": [
                    {"name": "id", "required": True, "value": identifier},
                    {"name": "methodType", "required": False, "value": method_type},
                ]
            }
        },
    }


def select_authenticator(base: str, *labels: str) -> dict[str, Any]:
    ids = {"Password": PASSWORD_AUTHENTICATOR_ID, "Email": EMAIL_AUTHENTICATOR_ID}
    types = {"Password": "password", "Email": "email"}
    return remediation(
        "select-authenticator-authenticate",
        base,
        "/idp/idx/challenge",
        [{"name": "authenticator", "type": "object",
          "options": [authenticator_option(label, types[label], ids[label]) for label in labels]}],
    )


def idx_body(base: str, *remediations: dict[str, Any]) -> dict[str, Any]:
    return {"version": "1.0.0", "stateHandle": STATE_HANDLE,
            "remediation": {"type": "array", "value": list(remediations)}}


def idx_error(message: str) -> dict[str, Any]:
    return {"version": "1.0.0", "stateHandle": STATE_HANDLE,
            "messages": {"type": "array", "value": [{"message": message, "class": "ERROR"}]}}


def idx_success() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "successWithInteractionCode": {
            "name": "issue",
            "href": "https://login.example/oauth2/default/v1/token",
            "method": "POST",
            "value": [
                {"name": "grant_type", "value": "interaction_code"},
                {"name": "interaction_code", "value": INTERACTION_CODE},
            ],
        },
    }


def tokens_payload(access: str, refresh: str) -> dict[str, Any]:
    return {
        "token_type": "Bearer",
        "expires_in": 3600,
        "access_token": access,
        "refresh_token": refresh,
        "scope": "openid email profile offline_access",
        "id_token": "id.token.x",
    }


@pytest.fixture
def okta_ok(server: FakeServer) -> FakeServer:
    """An Identity Engine that accepts USERNAME/PASSWORD and issues ACCESS/REFRESH."""
    base = server.url

    server.json("/oauth2/default/v1/interact", {"interaction_handle": INTERACTION_HANDLE}, method="POST")
    server.json(
        "/idp/idx/introspect",
        idx_body(base, remediation("identify", base, "/idp/idx/identify",
                                   [{"name": "identifier", "label": "Email", "required": True}])),
        method="POST",
    )
    # The real org offers the password challenge straight after identify, with
    # the authenticator picker alongside it.
    server.json(
        "/idp/idx/identify",
        idx_body(
            base,
            remediation("challenge-authenticator", base, "/idp/idx/challenge/answer",
                        [{"name": "credentials", "type": "object",
                          "form": {"value": [{"name": "passcode", "label": "Wachtwoord", "secret": True}]}}]),
            select_authenticator(base, "Email", "Password"),
        ),
        method="POST",
    )

    def answer(_request: web.Request) -> web.Response:
        body = server.jsons[-1]
        if body.get("credentials", {}).get("passcode") == PASSWORD and body.get("stateHandle") == STATE_HANDLE:
            return web.json_response(idx_success())
        return web.json_response(idx_error("Authenticatie mislukt"), status=401)

    def token(_request: web.Request) -> web.Response:
        form = server.forms[-1]
        grant = form.get("grant_type")
        if grant == "interaction_code" and form.get("interaction_code") == INTERACTION_CODE and form.get("code_verifier"):
            return web.json_response(tokens_payload(ACCESS, REFRESH))
        if grant == "authorization_code" and form.get("code") == CODE and form.get("code_verifier"):
            return web.json_response(tokens_payload(ACCESS, REFRESH))
        if grant == "refresh_token" and form.get("refresh_token") == REFRESH:
            return web.json_response(tokens_payload("okta-access-2", "okta-refresh-2"))
        if grant == "password":
            return web.json_response(
                {"error": "unsupported_grant_type", "error_description": "not enabled"}, status=400
            )
        return web.json_response({"error": "invalid_grant"}, status=400)

    def authorize(request: web.Request) -> web.Response:
        """The browser flow only; Identity Engine serves HTML to anything else."""
        query = request.query
        assert query["code_challenge_method"] == "S256"
        location = f"{REDIRECT}?{urlencode({'code': CODE, 'state': query['state']})}"
        return web.Response(status=302, headers={"Location": location})

    server.handle("POST", "/idp/idx/challenge/answer", answer)
    server.handle("POST", "/oauth2/default/v1/token", token)
    server.handle("GET", "/oauth2/default/v1/authorize", authorize)
    return server


@pytest.fixture
def okta_mfa(okta_ok: FakeServer) -> FakeServer:
    """ENGIE's real shape: the password is accepted, then an emailed code is required.

    One handler serves both answers because Okta uses the same href for the
    password and for the code; the passcode value is what tells them apart.
    """
    base = okta_ok.url

    def answer(_request: web.Request) -> web.Response:
        passcode = okta_ok.jsons[-1].get("credentials", {}).get("passcode")
        if passcode == PASSWORD:
            return web.json_response(idx_body(base, select_authenticator(base, "Email")))
        if passcode == EMAIL_CODE:
            return web.json_response(idx_success())
        return web.json_response(idx_error("Ongeldige code"), status=401)

    def challenge(_request: web.Request) -> web.Response:
        """Selecting the email authenticator makes Okta send the mail and ask for the code."""
        return web.json_response(
            idx_body(base, remediation("challenge-authenticator", base, "/idp/idx/challenge/answer",
                                       [{"name": "credentials", "type": "object",
                                         "form": {"value": [{"name": "passcode", "secret": True}]}}]))
        )

    okta_ok.handle("POST", "/idp/idx/challenge/answer", answer)
    okta_ok.handle("POST", "/idp/idx/challenge", challenge)
    return okta_ok


@pytest_asyncio.fixture
async def auth(server: FakeServer) -> AsyncIterator[OktaAuth]:
    """An OktaAuth pointed at the loopback server, closed with the test.

    It owns its aiohttp session, so without the teardown every test that makes
    a request leaks one and aiohttp prints "Unclosed client session".
    """
    instance = OktaAuth(
        client_id=CLIENT_ID,
        issuer=f"{server.url}/oauth2/default",
        org_url=server.url,
        redirect_uri=REDIRECT,
        timeout=5,
    )
    yield instance
    await instance.close()


@pytest.fixture
def tokens() -> TokenSet:
    return TokenSet(access_token=ACCESS, refresh_token=REFRESH, expires_at=9_999_999_999.0)


@pytest_asyncio.fixture
async def client(server: FakeServer, auth: OktaAuth, tokens: TokenSet) -> AsyncIterator[EngieClient]:
    async with EngieClient(tokens, auth=auth, base_url=server.url, timeout=5) as c:
        yield c


@pytest_asyncio.fixture
async def writer(server: FakeServer, auth: OktaAuth, tokens: TokenSet) -> AsyncIterator[EngieClient]:
    """The same client with the write gate open, for the endpoints that change the account."""
    async with EngieClient(tokens, auth=auth, base_url=server.url, timeout=5, allow_writes=True) as c:
        yield c


def query_of(request: web.Request) -> dict[str, list[str]]:
    return parse_qs(request.query_string, keep_blank_values=True)


