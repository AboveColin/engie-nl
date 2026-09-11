"""The P1 dongle, which is a Net2Grid device on a Net2Grid host.

Nothing here goes through the gateway. The dongle's host has its own API key,
its own bearer, and its own idea of what a 401 means, so it gets its own client
and its own tests.
"""

from __future__ import annotations

import pytest

from engie_nl import EngieApiError, EngieAuthError, Net2GridClient, P1Client
from engie_nl.constants import NET2GRID_API_KEY
from engie_nl.generated import MeterStatusResponse, P1TokenResponse

from tests.conftest import FakeServer

OKTA_ACCESS = "okta-access-1"
N2G_ACCESS = "n2g-access-1"


async def test_exchange_token_trades_an_engie_session_for_a_net2grid_one(server: FakeServer) -> None:
    """Net2Grid does not know the password; it trusts the Okta access token."""
    server.json("/v3/sso/exchange-token", {"access_token": N2G_ACCESS, "expires_in": 3600}, method="POST")
    async with Net2GridClient(base_url=server.url, timeout=5) as client:
        session = await client.exchange_token(OKTA_ACCESS)
    assert isinstance(session, P1TokenResponse)
    assert session.access_token == N2G_ACCESS
    assert server.jsons[-1] == {"external_provider_access_token": OKTA_ACCESS}
    # The key is compiled into the public APK and identifies the app, not a person.
    assert server.requests[-1].headers["X-Api-Key"] == NET2GRID_API_KEY
    assert "Authorization" not in server.requests[-1].headers


async def test_introspect_sso_user_sends_the_same_trade_on_the_signup_path(
    server: FakeServer,
) -> None:
    server.json("/v3/registration/introspection/sso-user", {"access_token": N2G_ACCESS}, method="POST")
    async with Net2GridClient(base_url=server.url, timeout=5) as client:
        session = await client.introspect_sso_user(OKTA_ACCESS)
    assert isinstance(session, P1TokenResponse)
    assert server.jsons[-1] == {"external_provider_access_token": OKTA_ACCESS}


async def test_meter_connection_sends_the_net2grid_bearer(server: FakeServer) -> None:
    server.json("/v3/smart-bridge/meter-connection", {"connected": True})
    async with Net2GridClient(base_url=server.url, timeout=5) as client:
        status = await client.meter_connection(N2G_ACCESS)
    assert isinstance(status, MeterStatusResponse)
    assert server.requests[-1].headers["Authorization"] == f"Bearer {N2G_ACCESS}"


async def test_a_non_object_body_becomes_none(server: FakeServer) -> None:
    """Every one of the three reads parses an object or gives up; none of them guesses."""
    server.json("/v3/sso/exchange-token", [], method="POST")
    server.json("/v3/registration/introspection/sso-user", [], method="POST")
    server.json("/v3/smart-bridge/meter-connection", [])
    async with Net2GridClient(base_url=server.url, timeout=5) as client:
        assert await client.exchange_token(OKTA_ACCESS) is None
        assert await client.introspect_sso_user(OKTA_ACCESS) is None
        assert await client.meter_connection(N2G_ACCESS) is None


async def test_a_401_is_an_auth_error_and_the_rest_is_an_api_error(server: FakeServer) -> None:
    server.json("/v3/smart-bridge/meter-connection", {"message": "bad token"}, status=401)
    server.json("/v3/sso/exchange-token", {"message": "nope"}, status=403, method="POST")
    async with Net2GridClient(base_url=server.url, timeout=5) as client:
        with pytest.raises(EngieAuthError, match="Net2Grid rejected the token"):
            await client.meter_connection("not-a-token")
        with pytest.raises(EngieApiError) as err:
            await client.exchange_token(OKTA_ACCESS)
    assert err.value.status == 403
    assert err.value.detail == "nope"


async def test_a_custom_api_key_reaches_the_host(server: FakeServer) -> None:
    server.json("/v3/smart-bridge/meter-connection", {"connected": False})
    async with Net2GridClient(base_url=server.url, api_key="n2g-key-0", timeout=5) as client:
        await client.meter_connection(N2G_ACCESS)
    assert server.requests[-1].headers["X-Api-Key"] == "n2g-key-0"


async def test_p1_client_is_the_same_client_under_the_name_on_the_box(server: FakeServer) -> None:
    """ENGIE sells it as "de ENGIE P1 module", so both names have to work."""
    server.json("/v3/smart-bridge/meter-connection", {"connected": True})
    async with P1Client(base_url=server.url, timeout=5) as client:
        assert isinstance(client, Net2GridClient)
        assert await client.meter_connection(N2G_ACCESS) is not None
