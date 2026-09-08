"""Happy Hour: windows when ENGIE pays for using more, not less.

ENGIE announces an hour, the customer subscribes, and consumption above the
usual baseline in that hour earns a reward.
"""

from __future__ import annotations

from typing import Any

from ..generated import HappyHourSessionDTO, HappyHoursResponse, HappyHourSubscriptionModel
from ._base import ApiGroup, parse_list, parse_one


class HappyHourApi(ApiGroup):
    """``client.happy_hour``: announced hours, subscriptions and results."""

    async def hours(self) -> HappyHoursResponse | None:
        """``GET /api/v1/happyhours``: the announced windows."""
        return parse_one(await self._get("/api/v1/happyhours"), HappyHoursResponse.from_api)

    async def sessions(self) -> list[HappyHourSessionDTO]:
        """``GET /api/v1/happyhour/sessions``: what each past hour earned."""
        return parse_list(await self._get("/api/v1/happyhour/sessions"), HappyHourSessionDTO.from_api)

    async def subscriptions(self) -> list[HappyHourSubscriptionModel]:
        """``GET /api/v1/assets/happyhour``: which hours the customer signed up for."""
        return parse_list(await self._get("/api/v1/assets/happyhour"), HappyHourSubscriptionModel.from_api)

    async def subscribe(self, body: Any) -> Any:
        """``POST /api/v1/assets/happyhour``."""
        return await self._write("POST", "/api/v1/assets/happyhour", json_body=body)

    async def unsubscribe(self, subscription_id: str) -> Any:
        """``DELETE /api/v1/assets/happyhour/{id}``."""
        return await self._write("DELETE", f"/api/v1/assets/happyhour/{subscription_id}")

    async def request_payout(self) -> Any:
        """``POST /api/v1/happyhour/payout``: pay out the reward earned."""
        return await self._write("POST", "/api/v1/happyhour/payout")
