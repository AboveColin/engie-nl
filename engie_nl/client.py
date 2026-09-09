"""Async client for the ENGIE Energie NL gateway.

Example::

    import asyncio
    from engie_nl import EngieClient, OktaAuth

    async def main():
        async with OktaAuth() as auth:
            tokens = await auth.login("user@example.com", "password")
            async with EngieClient(tokens, auth=auth) as client:
                user = await client.get_user()
                for series in await client.get_consumptions(user.eans, days=7):
                    for day in series.data:
                        print(series.ean, day.day, day.total)

    asyncio.run(main())

The client sends the four headers the app sends and the Okta access token as
the bearer. When the token is within :data:`TOKEN_REFRESH_MARGIN` of expiry, or
the gateway answers 401, it refreshes once through the :class:`OktaAuth` it was
given and calls ``on_tokens_updated`` so the caller can persist the new pair.

The methods on the client itself are the reads a household polls. The rest of
the mapped API, 148 verb+path pairs in all, hangs off it in groups:
``client.tariffs``, ``client.meter``, ``client.billing``, ``client.account``,
``client.mandates``, ``client.assets``, ``client.enode``,
``client.smart_charging``, ``client.happy_hour``, ``client.solar``,
``client.address``, ``client.support`` and ``client.ev``.

Anything that changes the account is refused unless the client was built with
``allow_writes=True``. See :class:`~engie_nl.exceptions.EngieWriteBlocked`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from datetime import date, timedelta
from typing import Any

import aiohttp

from ._http import SessionOwner, send
from ._parse import Params, as_dicts, eans_param
from .api import (
    AccountApi,
    AddressApi,
    AssetsApi,
    BillingApi,
    EnodeApi,
    EvApi,
    HappyHourApi,
    LegacyApi,
    MandatesApi,
    MeterApi,
    SmartChargingApi,
    SolarApi,
    SupportApi,
    TariffsApi,
)
from .auth import OktaAuth, TokenSet
from .constants import (
    DATE_FORMAT,
    DEFAULT_TIMEOUT,
    REQUEST_ATTEMPTS,
    RETRY_BACKOFF_SECONDS,
    GATEWAY_HEADERS,
    GATEWAY_URL,
    PATH_CONSUMPTIONS,
    PATH_DAY_AHEAD,
    PATH_DOCUMENTS,
    PATH_ESTIMATIONS,
    PATH_MANDATES,
    PATH_MER_PERIODS,
    PATH_METER_READINGS,
    PATH_OPENING_HOURS,
    PATH_OUTAGES,
    PATH_TRANSACTIONS,
    PATH_USER,
)
from .exceptions import (
    EngieApiError,
    EngieAuthError,
    EngieNetworkError,
    EngieRateLimited,
    EngieWriteBlocked,
)
from .models import (
    ConsumptionSeries,
    DayAheadPrice,
    DocumentRef,
    EnergyType,
    EstimationCosts,
    Mandate,
    MerPeriod,
    MeterReadings,
    OutageMessage,
    Transaction,
    User,
)

TokensCallback = Callable[[TokenSet], Awaitable[None] | None]


def _fmt(day: date) -> str:
    return day.strftime(DATE_FORMAT)


def _window(start: date | None, end: date | None, days: int) -> tuple[date, date]:
    end = end or date.today()
    start = start or end - timedelta(days=days)
    if start > end:
        raise ValueError("start must not be after end")
    return start, end


class EngieClient(SessionOwner):
    """Reads a customer's data from ``prod-egw.engie-app.nl``."""

    def __init__(
        self,
        tokens: TokenSet,
        *,
        auth: OktaAuth | None = None,
        session: aiohttp.ClientSession | None = None,
        on_tokens_updated: TokensCallback | None = None,
        base_url: str = GATEWAY_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_backoff: float = RETRY_BACKOFF_SECONDS,
        allow_writes: bool = False,
    ) -> None:
        super().__init__(session, timeout)
        self._retry_backoff = retry_backoff
        self.allow_writes = allow_writes
        self.tokens: TokenSet = tokens
        self._auth = auth
        self._on_tokens_updated = on_tokens_updated
        self._base_url = base_url.rstrip("/")
        self._refresh_lock = asyncio.Lock()

        self.account = AccountApi(self)
        self.address = AddressApi(self)
        self.assets = AssetsApi(self)
        self.billing = BillingApi(self)
        self.enode = EnodeApi(self)
        self.ev = EvApi(self)
        self.happy_hour = HappyHourApi(self)
        self.legacy = LegacyApi(self)
        self.mandates = MandatesApi(self)
        self.meter = MeterApi(self)
        self.smart_charging = SmartChargingApi(self)
        self.solar = SolarApi(self)
        self.support = SupportApi(self)
        self.tariffs = TariffsApi(self)

    async def __aenter__(self) -> EngieClient:
        return self

    # --- auth plumbing -------------------------------------------------------

    async def refresh_tokens(self) -> TokenSet:
        """Refresh through Okta and publish the new pair. Serialized: one refresh at a time."""
        if self._auth is None:
            raise EngieAuthError("access token expired and no OktaAuth was given to refresh it")
        async with self._refresh_lock:
            new = await self._auth.refresh(self.tokens)
            self.tokens = new
            if self._on_tokens_updated is not None:
                result = self._on_tokens_updated(new)
                if result is not None:
                    await result
            return new

    async def _headers(self) -> dict[str, str]:
        if self.tokens.is_expired() and self._auth is not None:
            await self.refresh_tokens()
        return {**GATEWAY_HEADERS, "Authorization": f"Bearer {self.tokens.access_token}"}

    async def _get(self, path: str, params: Params | None = None) -> Any:
        """GET one path, retrying when the gateway does not answer.

        Measured 2026-09-07 against the live gateway: its latency is erratic and
        not tied to the endpoint, the headers or the client. ``/api/v1/user``
        answered in 0.62 s, then twice not at all within 45 s, then in 0.49 s,
        with identical headers inside one minute. ``/api/v1/documents`` took
        12.5 s once and 0.14 s otherwise. Every stall came after the request
        headers were sent, with DNS and connect both under 0.1 s, so nothing
        local explains it.

        One attempt therefore loses a poll often enough to matter. A timeout is
        retried; a real answer, including an error status, is not, because the
        gateway means those.
        """
        return await self._request("GET", path, params=params)

    async def _write(
        self,
        verb: str,
        path: str,
        *,
        params: Params | None = None,
        form: Params | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Send a request that changes the account, if this client may.

        The gate is here rather than in each method so a new endpoint cannot
        forget it. Two POSTs are queries despite the verb and call
        :meth:`_request` directly: ``/api/v1/readings`` and
        ``/api/v1/p4-errors`` both send a body to read P4 data back.
        """
        if not self.allow_writes:
            raise EngieWriteBlocked(
                f"{verb} {path} changes the account; "
                "construct EngieClient(..., allow_writes=True) to permit it"
            )
        return await self._request(verb, path, params=params, form=form, json_body=json_body, headers=headers)

    async def _request(
        self,
        verb: str,
        path: str,
        *,
        params: Params | None = None,
        form: Params | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        attempt = 0
        while True:
            attempt += 1
            try:
                return await self._request_once(
                    verb, path, params=params, form=form, json_body=json_body, headers=headers
                )
            except EngieRateLimited:
                # Answering "slow down" with three quick retries is how a short
                # block becomes a long one. The next poll is the retry.
                raise
            except EngieNetworkError:
                if attempt >= REQUEST_ATTEMPTS:
                    raise
                await asyncio.sleep(self._retry_backoff * attempt)

    async def _request_once(
        self,
        verb: str,
        path: str,
        *,
        params: Params | None = None,
        form: Params | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
        retry_on_401: bool = True,
    ) -> Any:
        session = await self._get_session()
        status, body = await send(
            session,
            verb,
            f"{self._base_url}{path}",
            params=params,
            form=form,
            json_body=json_body,
            headers={**await self._headers(), **(headers or {})},
            timeout=self._timeout,
        )
        if status == 401 and retry_on_401 and self._auth is not None:
            await self.refresh_tokens()
            return await self._request_once(
                verb, path, params=params, form=form, json_body=json_body,
                headers=headers, retry_on_401=False,
            )
        if status == 401:
            raise EngieAuthError("the gateway rejected the access token")
        if status == 429:
            raise EngieRateLimited(f"{verb} {path}: the gateway asked for fewer requests")
        if status >= 400:
            raise EngieApiError(f"{verb} {path} failed", status=status, body=body)
        return body

    # --- reads ---------------------------------------------------------------

    async def get_user(self) -> User:
        """``GET /api/v1/user``: customer, contact details, addresses and EANs."""
        data = await self._get(PATH_USER)
        if not isinstance(data, dict):
            raise EngieApiError("unexpected /user body", status=200, body=data)
        return User.from_api(data)

    async def get_consumptions(
        self,
        eans: Iterable[str] | str,
        *,
        start: date | None = None,
        end: date | None = None,
        days: int = 30,
    ) -> list[ConsumptionSeries]:
        """Daily consumption per EAN. Defaults to the last ``days`` days up to today."""
        start, end = _window(start, end, days)
        params: Params = [("from", _fmt(start)), ("to", _fmt(end)), *eans_param(eans)]
        data = await self._get(PATH_CONSUMPTIONS, params)
        return [ConsumptionSeries.from_api(d) for d in as_dicts(data)]

    async def get_meter_readings(
        self,
        eans: Iterable[str] | str,
        *,
        start: date | None = None,
        end: date | None = None,
        days: int = 400,
    ) -> list[MeterReadings]:
        """Meter readings (meterstanden) per EAN and register."""
        start, end = _window(start, end, days)
        params: Params = [*eans_param(eans), ("start_date", _fmt(start)), ("end_date", _fmt(end))]
        data = await self._get(PATH_METER_READINGS, params)
        return [MeterReadings.from_api(d) for d in as_dicts(data)]

    async def get_estimations(self, eans: Iterable[str] | str, *, amount: int) -> EstimationCosts:
        """Termijnbedrag advice for the given monthly ``amount`` in whole euros."""
        params: Params = [("amount", str(int(amount))), *eans_param(eans)]
        data = await self._get(PATH_ESTIMATIONS, params)
        if not isinstance(data, dict):
            raise EngieApiError("unexpected /estimations body", status=200, body=data)
        return EstimationCosts.from_api(data)

    async def get_transactions(self) -> list[Transaction]:
        """Invoices and payments."""
        data = await self._get(PATH_TRANSACTIONS)
        items = data.get("transactions") if isinstance(data, dict) else data
        return [Transaction.from_api(d) for d in as_dicts(items)]

    async def get_documents(self) -> list[DocumentRef]:
        """Document references (invoices, contracts); the PDF itself is ``/api/v2/document/{ref}``."""
        data = await self._get(PATH_DOCUMENTS)
        items = data.get("documents") if isinstance(data, dict) else data
        return [DocumentRef.from_api(d) for d in as_dicts(items)]

    async def get_mandates(self, eans: Iterable[str] | str) -> list[Mandate]:
        """Smart-meter data mandate status per EAN."""
        data = await self._get(PATH_MANDATES, eans_param(eans))
        return [Mandate.from_api(d) for d in as_dicts(data)]

    async def get_outages(self, customer_id: str | None = None) -> list[OutageMessage]:
        """Storingen and maintenance notices, optionally filtered to one customer."""
        params: Params = [("customerId", customer_id)] if customer_id else []
        data = await self._get(PATH_OUTAGES, params or None)
        return [OutageMessage.from_api(d) for d in as_dicts(data)]

    async def get_day_ahead_prices(
        self,
        energy_type: EnergyType | str = EnergyType.ELECTRICITY,
        *,
        start: date | None = None,
        end: date | None = None,
    ) -> list[DayAheadPrice]:
        """Dynamic day-ahead prices. Defaults to today and tomorrow."""
        start = start or date.today()
        end = end or start + timedelta(days=1)
        params: Params = [("type", str(energy_type)), ("start_date", _fmt(start)), ("end_date", _fmt(end))]
        data = await self._get(PATH_DAY_AHEAD, params)
        return [DayAheadPrice.from_api(d) for d in as_dicts(data)]

    async def get_mer_periods(self) -> list[MerPeriod]:
        """Periods for which a monthly energy report (MER) exists."""
        data = await self._get(PATH_MER_PERIODS)
        return [MerPeriod.from_api(d) for d in as_dicts(data)]

    async def get_opening_hours(self) -> Any:
        """Customer service opening hours, returned raw (no model yet)."""
        return await self._get(PATH_OPENING_HOURS)
