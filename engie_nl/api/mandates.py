"""The smart-meter data mandate (machtiging slimme meterdata).

Reading the current state is on the client itself as
:meth:`~engie_nl.client.EngieClient.get_mandates`. Granting and withdrawing are
here, because both change what ENGIE is allowed to collect.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..generated import ApprovalData
from ._base import ApiGroup, Params, eans_param, parse_list


class MandatesApi(ApiGroup):
    """``client.mandates``: grant or withdraw permission to read the meter."""

    async def grant(self, eans: Iterable[str] | str, *, current_version: str) -> list[ApprovalData]:
        """``POST /api/v1/mandates``: accept the current mandate text.

        ``current_version`` is the version of the terms being accepted, which
        ENGIE records with the consent.
        """
        form: Params = [*eans_param(eans), ("currentVersion", current_version)]
        return parse_list(await self._write("POST", "/api/v1/mandates", form=form), ApprovalData.from_api)

    async def withdraw(self, eans: Iterable[str] | str) -> None:
        """``POST /api/v1/withdraw-mandates``: stop the daily meter feed.

        ENGIE then reads the meter far less often, so consumption data thins
        out. The app declares this path on two of its interfaces.
        """
        await self._write("POST", "/api/v1/withdraw-mandates", form=eans_param(eans))
