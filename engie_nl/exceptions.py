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

    def __str__(self) -> str:
        return f"{self.message} (HTTP {self.status})"


class EngieNetworkError(EngieError):
    """Timeouts, connection failures and TLS errors."""
