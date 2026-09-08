"""Meter readings: filing them, deleting them, and the P4 feed behind them.

Reading meterstanden is on the client itself as
:meth:`~engie_nl.client.EngieClient.get_meter_readings`. What is here is the
rest: two queries that use POST, and the writes.
"""

from __future__ import annotations

from datetime import date
from typing import Any
from collections.abc import Iterable

from ..constants import DATE_FORMAT
from ..generated import P4, P4StatusResponse
from ._base import ApiGroup, Params, eans_param, parse_list


class MeterApi(ApiGroup):
    """``client.meter``: everything about meterstanden except reading them."""

    # --- queries that use POST -----------------------------------------------

    async def p4_readings(self, body: Any) -> list[P4]:
        """``POST /api/v1/readings``: the smart-meter feed for a period.

        A POST that reads. The body carries the EANs and the window, which is
        too long for a query string, so the gateway takes it as JSON. No write
        gate applies.
        """
        return parse_list(await self._query("POST", "/api/v1/readings", json_body=body), P4.from_api)

    async def p4_errors(self, body: Any) -> list[P4StatusResponse]:
        """``POST /api/v1/p4-errors``: why a day of P4 data is missing.

        The app calls this when a day has no reading, to tell "the meter did not
        report" apart from "ENGIE has not processed it yet". Also a POST that
        reads.
        """
        return parse_list(
            await self._query("POST", "/api/v1/p4-errors", json_body=body), P4StatusResponse.from_api
        )

    # --- writes --------------------------------------------------------------

    async def add_readings(self, body: Any) -> Any:
        """``POST /api/v1/meterstands``: file a meter reading with ENGIE.

        This is a real submission to the supplier who bills the account. A wrong
        value here becomes a wrong invoice.
        """
        return await self._write("POST", "/api/v1/meterstands", json_body=body)

    async def delete_readings(self, eans: Iterable[str] | str, *, day: date) -> Any:
        """``DELETE /api/v1/meterstands``: withdraw the readings filed for one date."""
        params: Params = [("date", day.strftime(DATE_FORMAT)), *eans_param(eans)]
        return await self._write("DELETE", "/api/v1/meterstands", params=params)

    async def activate_dongle(self, dongle_id: str) -> Any:
        """``POST /api/v1/p1/activate``: tie a P1 dongle to this account.

        On the gateway, not on Net2Grid: ENGIE records the pairing, the dongle
        itself is reached through :class:`~engie_nl.net2grid.Net2GridClient`.
        """
        return await self._write("POST", "/api/v1/p1/activate", form=[("dongle_id", dongle_id)])

    async def register_dongle(self, body: Any) -> Any:
        """``POST /api/v1/p1/register``: enrol for a dongle before it ships."""
        return await self._write("POST", "/api/v1/p1/register", json_body=body)

    async def request_correction(self, body: Any) -> Any:
        """``POST /api/v1/meterstands/correction-request``: ask ENGIE to fix a reading."""
        return await self._write("POST", "/api/v1/meterstands/correction-request", json_body=body)
