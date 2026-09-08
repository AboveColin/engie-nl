"""Electric-vehicle sales requests.

Four lead forms. None of them reads anything; each creates a request that a
person at ENGIE follows up.
"""

from __future__ import annotations

from typing import Any

from ._base import ApiGroup


class EvApi(ApiGroup):
    """``client.ev``: charge cards, charging stations and white papers."""

    async def request_charge_card(self, body: Any) -> Any:
        """``POST /api/v1/ev/charge-card-requests``."""
        return await self._write("POST", "/api/v1/ev/charge-card-requests", json_body=body)

    async def request_charging_station_contact(self, body: Any) -> Any:
        """``POST /api/v1/ev/charging-station-contact-requests``."""
        return await self._write("POST", "/api/v1/ev/charging-station-contact-requests", json_body=body)

    async def request_charging_station_quote(self, body: Any) -> Any:
        """``POST /api/v2/ev/charging-station-quotation-requests``."""
        return await self._write("POST", "/api/v2/ev/charging-station-quotation-requests", json_body=body)

    async def request_white_paper(self, body: Any) -> Any:
        """``POST /api/v1/ev/white-paper-requests``."""
        return await self._write("POST", "/api/v1/ev/white-paper-requests", json_body=body)
