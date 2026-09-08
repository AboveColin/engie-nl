"""Contract tariffs.

The day-ahead prices of a dynamic contract are on the client itself as
:meth:`~engie_nl.client.EngieClient.get_day_ahead_prices`. This group is the
other endpoint: the rates the customer's own contract charges.
"""

from __future__ import annotations

from datetime import date
from typing import Any
from collections.abc import Iterable

from ..constants import DATE_FORMAT
from ..generated import MGWTariffsResponse
from ._base import ApiGroup, Params, eans_param, parse_one


class TariffsApi(ApiGroup):
    """``client.tariffs``: what this contract charges per kWh, m3 and day."""

    async def get(
        self,
        eans: Iterable[str] | str,
        *,
        start: date,
        end: date,
    ) -> MGWTariffsResponse | None:
        """``GET /api/v1/tariffs?date_from=&date_to=&eans[]=``.

        Returns ``tariffs`` (one entry per EAN, tariff type and period, with
        ``price_ex``, ``tax``, ``unit_of_measure`` and ``use_for_feed_in``) and
        ``types`` (which period is single-tariff).

        This is the contract's own rates, not the market's. It is the endpoint
        to check a signed contract against, because the ``tariffs`` block inside
        ``/api/v1/user`` is all zeros until delivery starts.

        Both dates are required: without them the gateway answers HTTP 422 and
        names the missing fields. Before a contract's start date it answers HTTP
        400 "Request contains EAN (...) that does not belong to the user", the
        same refusal /consumptions gives as ``not-owned`` (measured
        2026-09-08, two days before delivery).
        """
        params: Params = [
            ("date_from", start.strftime(DATE_FORMAT)),
            ("date_to", end.strftime(DATE_FORMAT)),
            *eans_param(eans),
        ]
        return parse_one(await self._get("/api/v1/tariffs", params), MGWTariffsResponse.from_api)

    async def set_for_address(self, address_id: str, body: Any) -> Any:
        """``PUT /api/v1/tariffs/{addressId}``: file the rates for an address."""
        return await self._write("PUT", f"/api/v1/tariffs/{address_id}", json_body=body)
