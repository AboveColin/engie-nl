"""The ENGIE P1 dongle, which is a Net2Grid device on a Net2Grid host.

The dongle plugs into the meter's P1 port and reports live power, which is data
the gateway never has: ``/api/v1/consumptions`` is yesterday at best. It does
not go through ``prod-egw.engie-app.nl`` at all. It has its own host, its own
API key baked into the app, and its own bearer, which the customer's Okta access
token is exchanged for.

The exchange is the only part that touches both systems::

    async with OktaAuth() as auth:
        tokens = await auth.login(username, password)
    async with Net2GridClient() as p1:
        session = await p1.exchange_token(tokens.access_token)
        status = await p1.meter_connection(session.access_token)

Only ``/v3/smart-bridge/meter-connection`` is mapped as a read, because that is
all the app calls. The device's own live-power stream is not in the app's code
and is not mapped here.
"""

from __future__ import annotations

from typing import Any

import aiohttp

from ._http import SessionOwner, send
from .constants import DEFAULT_TIMEOUT, NET2GRID_API_KEY, NET2GRID_URL
from .exceptions import EngieApiError, EngieAuthError
from .generated import MeterStatusResponse, P1TokenResponse


class Net2GridClient(SessionOwner):
    """Reads the P1 dongle's status from ``api.n2g-engie-nl-gen2.net``."""

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession | None = None,
        base_url: str = NET2GRID_URL,
        api_key: str = NET2GRID_API_KEY,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(session, timeout)
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def __aenter__(self) -> Net2GridClient:
        return self

    async def exchange_token(self, okta_access_token: str) -> P1TokenResponse | None:
        """``POST /v3/sso/exchange-token``: an ENGIE session becomes a Net2Grid one.

        Net2Grid does not know the customer's password. It trusts the Okta
        access token, checks it with ENGIE, and issues its own pair.
        """
        body = {"external_provider_access_token": okta_access_token}
        data = await self._request("POST", "/v3/sso/exchange-token", json_body=body)
        return P1TokenResponse.from_api(data) if isinstance(data, dict) else None

    async def introspect_sso_user(self, okta_access_token: str) -> P1TokenResponse | None:
        """``POST /v3/registration/introspection/sso-user``: the same trade during signup."""
        body = {"external_provider_access_token": okta_access_token}
        data = await self._request("POST", "/v3/registration/introspection/sso-user", json_body=body)
        return P1TokenResponse.from_api(data) if isinstance(data, dict) else None

    async def meter_connection(self, access_token: str) -> MeterStatusResponse | None:
        """``GET /v3/smart-bridge/meter-connection``: is the dongle talking to the meter."""
        data = await self._request("GET", "/v3/smart-bridge/meter-connection", token=access_token)
        return MeterStatusResponse.from_api(data) if isinstance(data, dict) else None

    async def _request(
        self,
        verb: str,
        path: str,
        *,
        json_body: Any = None,
        token: str | None = None,
    ) -> Any:
        session = await self._get_session()
        headers = {"X-Api-Key": self._api_key, "Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        status, body = await send(
            session,
            verb,
            f"{self._base_url}{path}",
            json_body=json_body,
            headers=headers,
            timeout=self._timeout,
        )
        if status == 401:
            raise EngieAuthError("Net2Grid rejected the token")
        if status >= 400:
            raise EngieApiError(f"{verb} {path} failed", status=status, body=body)
        return body


class P1Client(Net2GridClient):
    """Kept because the dongle is sold as "de ENGIE P1 module"."""
