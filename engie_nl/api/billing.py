"""Invoices, documents, the monthly amount and iDEAL payments."""

from __future__ import annotations

from typing import Any
from collections.abc import Iterable

from ..generated import (
    DocumentsResponse,
    MGWCreateIDealTransactionResponse,
    MGWUpdateIDealStatusResponse,
    PaymentInfo,
    PrepaymentResult,
)
from ._base import ApiGroup, Params, eans_param, parse_list, parse_one


class BillingApi(ApiGroup):
    """``client.billing``: what is owed, what was paid, and the paperwork."""

    # --- reads ---------------------------------------------------------------

    async def payment_status(self, invoice_id: str) -> PaymentInfo | None:
        """``GET /api/v1/transaction/{invoiceId}/payment``: the iDEAL state of one invoice."""
        data = await self._get(f"/api/v1/transaction/{invoice_id}/payment")
        return parse_one(data, PaymentInfo.from_api)

    async def document(self, ref_id: str) -> DocumentsResponse | None:
        """``GET /api/v2/document/{refId}``: the metadata for one document.

        The PDF itself is a separate download, not this JSON.
        """
        return parse_one(await self._get(f"/api/v2/document/{ref_id}"), DocumentsResponse.from_api)

    async def document_v1(self, ref_id: str) -> DocumentsResponse | None:
        """``GET /api/v1/document/{refId}``: the older path, still called in one place."""
        return parse_one(await self._get(f"/api/v1/document/{ref_id}"), DocumentsResponse.from_api)

    async def mer_report(self, period_id: str) -> Any:
        """``GET /api/v1/mer/periods/{id}/report``: the monthly energy report.

        The body is a file, not JSON, so it comes back as text. Use the raw
        response if you need the bytes.
        """
        return await self._get(f"/api/v1/mer/periods/{period_id}/report")

    async def ideal_status(self, transaction_id: str) -> MGWUpdateIDealStatusResponse | None:
        """``GET /api/v1/payments/ideal2/transactions/{id}/updatestatus``.

        Named "updatestatus" but it is a GET: it asks the payment provider where
        the transaction got to and returns the answer.
        """
        data = await self._get(f"/api/v1/payments/ideal2/transactions/{transaction_id}/updatestatus")
        return parse_one(data, MGWUpdateIDealStatusResponse.from_api)

    # --- writes --------------------------------------------------------------

    async def set_prepayment(self, eans: Iterable[str] | str, *, amount: int) -> list[PrepaymentResult]:
        """``PUT /api/v1/prepayment``: change the termijnbedrag collected each month.

        This changes a direct debit. Use
        :meth:`~engie_nl.client.EngieClient.get_estimations` first to see what
        ENGIE advises for the amount.
        """
        form: Params = [("amount", str(int(amount))), *eans_param(eans)]
        return parse_list(await self._write("PUT", "/api/v1/prepayment", form=form), PrepaymentResult.from_api)

    async def start_ideal_payment(self, body: Any) -> MGWCreateIDealTransactionResponse | None:
        """``POST /api/v1/payments/ideal2/transactions/new``: begin paying an invoice."""
        data = await self._write("POST", "/api/v1/payments/ideal2/transactions/new", json_body=body)
        return parse_one(data, MGWCreateIDealTransactionResponse.from_api)
