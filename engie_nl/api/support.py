"""Customer service, advice articles, feedback and the chat backend."""

from __future__ import annotations

from typing import Any

from ..generated import (
    AbstractBaseResponse,
    ArticlesResponse,
    CollectiveResponse,
    Measure,
    OpeningHoursResponse,
    SimpleStatus,
    WaitingTimes,
)
from ._base import ApiGroup, Params, parse_one


class SupportApi(ApiGroup):
    """``client.support``: opening hours, advice, feedback and chat."""

    # --- customer service ----------------------------------------------------

    async def opening_hours(self) -> OpeningHoursResponse | None:
        """``GET /api/v1/opening-hours``: when the phone line is staffed."""
        return parse_one(await self._get("/api/v1/opening-hours"), OpeningHoursResponse.from_api)

    async def waiting_time(self) -> WaitingTimes | None:
        """``GET /api/v1/opening-hours/waiting-time``: the queue right now."""
        return parse_one(await self._get("/api/v1/opening-hours/waiting-time"), WaitingTimes.from_api)

    # --- advice --------------------------------------------------------------

    async def advice_article(self, article_id: str) -> Measure | None:
        """``GET /api/v1/advice/articles/{id}``: one saving measure."""
        return parse_one(await self._get(f"/api/v1/advice/articles/{article_id}"), Measure.from_api)

    async def advice_changes(self, since_id: str) -> ArticlesResponse | None:
        """``GET /api/v1/advice/changes/{id}``: what changed since a known revision.

        The app keeps the articles in a local database and syncs the difference,
        which is why this takes a revision id rather than a page number.
        """
        return parse_one(await self._get(f"/api/v1/advice/changes/{since_id}"), ArticlesResponse.from_api)

    async def collective(self, *, campaign_id: str, broker_id: str) -> CollectiveResponse | None:
        """``GET /api/v1/collective``: the group-buying campaign behind a signup.

        **Gone from the server.** Measured 2026-09-08: HTTP 404 ``{"message":
        "The route api/v1/collective could not be found."}``.
        """
        params: Params = [("campaignId", campaign_id), ("brokerId", broker_id)]
        return parse_one(await self._get("/api/v1/collective", params), CollectiveResponse.from_api)

    # --- chat (Seamly) -------------------------------------------------------

    async def chat_categories(self, classification_id: str, *, profiles: str = "") -> AbstractBaseResponse | None:
        """``GET classifications/{classificationId}/categories``.

        Served by Seamly, the chat vendor, on its own host rather than the
        gateway. Pass a ``base_url`` to the client to reach it.
        """
        params: Params = [("dim.Profiles", profiles)] if profiles else []
        data = await self._get(f"classifications/{classification_id}/categories", params or None)
        return parse_one(data, AbstractBaseResponse.from_api)

    async def chat_event(self, event: str) -> Any:
        """``GET event/{event}``: report a chat lifecycle event to Seamly."""
        return await self._get(f"event/{event}")

    # --- writes --------------------------------------------------------------

    async def send_feedback(self, fields: dict[str, str]) -> SimpleStatus | None:
        """``POST /api/v1/feedback``: the in-app bug report.

        The app sends it as multipart with parts named ``feedback_type``,
        ``problem_description``, ``troubling_screen``, ``device``, ``os``,
        ``os_version`` and the retry flags. Sent here as a form, which the
        gateway accepts for the text-only case.
        """
        data = await self._write("POST", "/api/v1/feedback", form=list(fields.items()))
        return parse_one(data, SimpleStatus.from_api)

    async def submit_questionnaire(self, body: Any) -> Any:
        """``POST /api/v1/questionnaire``."""
        return await self._write("POST", "/api/v1/questionnaire", json_body=body)
