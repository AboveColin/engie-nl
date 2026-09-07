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

Every method here is a read. The gateway's write endpoints (meter readings,
prepayment, payment info, mandates, contract moves) are deliberately absent.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from datetime import date, timedelta
from typing import Any

import aiohttp

from ._http import SessionOwner, json_or_text
from .auth import OktaAuth, TokenSet
from .constants import (
    DATE_FORMAT,
    DEFAULT_TIMEOUT,
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
from .exceptions import EngieApiError, EngieAuthError, EngieNetworkError
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
Params = list[tuple[str, str]]


def _fmt(day: date) -> str:
    return day.strftime(DATE_FORMAT)


def _eans(eans: Iterable[str] | str) -> Params:
    values = [eans] if isinstance(eans, str) else list(eans)
    if not values:
        raise ValueError("at least one EAN is required")
    return [("eans[]", ean) for ean in values]


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
    ) -> None:
        super().__init__(session, timeout)
        self.tokens: TokenSet = tokens
        self._auth = auth
        self._on_tokens_updated = on_tokens_updated
        self._base_url = base_url.rstrip("/")
        self._refresh_lock = asyncio.Lock()

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

    async def _get(self, path: str, params: Params | None = None, *, retry_on_401: bool = True) -> Any:
        session = await self._get_session()
        url = f"{self._base_url}{path}"
        headers = await self._headers()
        try:
            async with session.get(url, params=params, headers=headers, timeout=self._timeout) as resp:
                body = await json_or_text(resp)
                status = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EngieNetworkError(f"GET {path} failed: {err}") from err
        if status == 401 and retry_on_401 and self._auth is not None:
            await self.refresh_tokens()
            return await self._get(path, params, retry_on_401=False)
        if status == 401:
            raise EngieAuthError("the gateway rejected the access token")
        if status >= 400:
            raise EngieApiError(f"GET {path} failed", status=status, body=body)
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
        params: Params = [("from", _fmt(start)), ("to", _fmt(end)), *_eans(eans)]
        data = await self._get(PATH_CONSUMPTIONS, params)
        return [ConsumptionSeries.from_api(d) for d in _as_list(data)]

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
        params: Params = [*_eans(eans), ("start_date", _fmt(start)), ("end_date", _fmt(end))]
        data = await self._get(PATH_METER_READINGS, params)
        return [MeterReadings.from_api(d) for d in _as_list(data)]

    async def get_estimations(self, eans: Iterable[str] | str, *, amount: int) -> EstimationCosts:
        """Termijnbedrag advice for the given monthly ``amount`` in whole euros."""
        params: Params = [("amount", str(int(amount))), *_eans(eans)]
        data = await self._get(PATH_ESTIMATIONS, params)
        if not isinstance(data, dict):
            raise EngieApiError("unexpected /estimations body", status=200, body=data)
        return EstimationCosts.from_api(data)

    async def get_transactions(self) -> list[Transaction]:
        """Invoices and payments."""
        data = await self._get(PATH_TRANSACTIONS)
        items = data.get("transactions") if isinstance(data, dict) else data
        return [Transaction.from_api(d) for d in _as_list(items)]

    async def get_documents(self) -> list[DocumentRef]:
        """Document references (invoices, contracts); the PDF itself is ``/api/v2/document/{ref}``."""
        data = await self._get(PATH_DOCUMENTS)
        items = data.get("documents") if isinstance(data, dict) else data
        return [DocumentRef.from_api(d) for d in _as_list(items)]

    async def get_mandates(self, eans: Iterable[str] | str) -> list[Mandate]:
        """Smart-meter data mandate status per EAN."""
        data = await self._get(PATH_MANDATES, _eans(eans))
        return [Mandate.from_api(d) for d in _as_list(data)]

    async def get_outages(self, customer_id: str | None = None) -> list[OutageMessage]:
        """Storingen and maintenance notices, optionally filtered to one customer."""
        params: Params = [("customerId", customer_id)] if customer_id else []
        data = await self._get(PATH_OUTAGES, params or None)
        return [OutageMessage.from_api(d) for d in _as_list(data)]

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
        return [DayAheadPrice.from_api(d) for d in _as_list(data)]

    async def get_mer_periods(self) -> list[MerPeriod]:
        """Periods for which a monthly energy report (MER) exists."""
        data = await self._get(PATH_MER_PERIODS)
        return [MerPeriod.from_api(d) for d in _as_list(data)]

    async def get_opening_hours(self) -> Any:
        """Customer service opening hours, returned raw (no model yet)."""
        return await self._get(PATH_OPENING_HOURS)


def _as_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [d for d in data["data"] if isinstance(d, dict)]
    return []
