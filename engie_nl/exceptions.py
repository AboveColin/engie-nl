"""Exception hierarchy for engie-nl.

A Home Assistant integration needs to tell three things apart: the credentials
are wrong or the session is gone (ask the user to log in again), the account
needs a second factor (a different flow), and the service is unreachable or
answered badly (retry later). Each gets its own type.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .auth import EmailChallenge


class EngieError(Exception):
    """Base class for every error raised by this package."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EngieAuthError(EngieError):
    """Okta rejected the credentials, or the token pair can no longer be refreshed."""


class EngieMfaRequiredError(EngieAuthError):
    """The Okta account requires a second factor.

    The password flow stops here. ``status`` is Okta's transaction status
    (for example ``MFA_REQUIRED`` or ``MFA_ENROLL``) and ``factors`` lists what
    Okta offered, so a caller can pick the browser flow with a clear message.
    """

    def __init__(self, message: str, status: str, factors: Optional[list[dict[str, Any]]] = None) -> None:
        super().__init__(message)
        self.status = status
        self.factors = factors or []


class EngieEmailCodeRequired(EngieAuthError):
    """The password was accepted and Okta has emailed a one-time code.

    This is not a rejection: the login is half done and the code is already in
    the mailbox. Hand ``challenge`` and the code to
    :meth:`~engie_nl.auth.OktaAuth.submit_email_code` to finish. Starting over
    instead sends a second code and invalidates this one.
    """

    def __init__(self, message: str, challenge: "EmailChallenge") -> None:
        super().__init__(message)
        self.challenge = challenge


class EngieApiError(EngieError):
    """The gateway answered with a non-success status.

    ``body`` is the decoded JSON when there was any, otherwise the raw text,
    so the caller can read ENGIE's own ``fault_string`` or ``error`` fields.
    """

    def __init__(self, message: str, status: int, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body

    @property
    def detail(self) -> str | None:
        """ENGIE's own explanation, whichever of its four shapes it arrived in.

        The gateway has no single error format. Measured 2026-09-07 and
        2026-09-08 on one account: ``{"message": "not-owned"}`` per EAN from
        /consumptions, ``{"message": "Request contains EAN (...) that does not
        belong to the user."}`` from /tariffs, ``{"fault_string":
        "TechnicalError", "detail": {...}}`` from /estimations, and a Laravel
        validation body ``{"message": ..., "errors": {"date_from": [...]}}``
        from /tariffs with no dates.
        """
        if not isinstance(self.body, dict):
            return str(self.body) if self.body else None
        errors = self.body.get("errors")
        if isinstance(errors, dict):
            flat = [str(m) for msgs in errors.values() for m in (msgs if isinstance(msgs, list) else [msgs])]
            if flat:
                return "; ".join(flat)
        for key in ("message", "fault_string", "error_description", "error"):
            value = self.body.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def __str__(self) -> str:
        detail = self.detail
        return f"{self.message} (HTTP {self.status}){f': {detail}' if detail else ''}"


class EngieNetworkError(EngieError):
    """Timeouts, connection failures and TLS errors."""


class EngieWriteBlocked(EngieError):
    """A method that changes the account was called on a read-only client.

    Every write is off by default. The endpoints behind them are not test
    fixtures: POST /api/v1/meterstands files a meter reading with the supplier
    who bills you, PUT /api/v1/prepayment changes the monthly amount collected
    by direct debit, and POST /api/v1/contract/move moves the contract to
    another address. A client that only reads can never fire one by accident.

    Pass ``allow_writes=True`` to :class:`~engie_nl.client.EngieClient` when a
    write is what you mean.
    """
