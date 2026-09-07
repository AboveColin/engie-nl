"""Endpoints, headers and app constants for the ENGIE Energie NL gateway.

Every value here was read from the decompiled Android app (nl.engie.engieapp
6.9.2, versionCode 404) on 2026-09-07. The map with receipts lives in the
apk-reverse-engineering repo under docs/engie-nl/ENGIE_NL_API.md.
"""

from __future__ import annotations

# --- the gateway ------------------------------------------------------------

GATEWAY_URL = "https://prod-egw.engie-app.nl"

# The app version the headers claim to be. The gateway may gate old versions
# (there is an EGWVersionBlock plugin in the app), so keep these in step with
# a version that is still in the Play Store.
APP_VERSION_NAME = "6.9.2"
APP_VERSION_CODE = "404"

# The app builds this from Build.* on the phone. The gateway sees only the
# shape, so a fixed, plausible device is fine.
USER_AGENT = (
    f"ENGIE/{APP_VERSION_NAME}-{APP_VERSION_CODE} "
    "(Linux; Android 14; Pixel 7 Build/UQ1A.240105.004) okhttp/4.12.0"
)

GATEWAY_HEADERS = {
    "X-Platform": "Android",
    "X-AppVersion": APP_VERSION_CODE,
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
}

# Dates in query strings. Responses carry ISO-8601 with an offset.
DATE_FORMAT = "%Y-%m-%d"

PATH_USER = "/api/v1/user"
PATH_CONSUMPTIONS = "/api/v1/consumptions"
PATH_METER_READINGS = "/api/v2/meterstands"
PATH_ESTIMATIONS = "/api/v1/estimations"
PATH_TRANSACTIONS = "/api/v1/transactions"
PATH_TRANSACTION_PAYMENT = "/api/v1/transaction/{invoice_id}/payment"
PATH_DOCUMENTS = "/api/v1/documents"
PATH_DOCUMENT = "/api/v2/document/{ref_id}"
PATH_MANDATES = "/api/v1/mandates"
PATH_OUTAGES = "/api/v1/outages"
PATH_MER_PERIODS = "/api/v1/mer/periods"
PATH_MER_REPORT = "/api/v1/mer/periods/{period_id}/report"
PATH_DAY_AHEAD = "/api/v1/tariffs/day-ahead"
PATH_OPENING_HOURS = "/api/v1/opening-hours"
PATH_WAITING_TIME = "/api/v1/opening-hours/waiting-time"

# --- Okta -------------------------------------------------------------------

OKTA_ORG_URL = "https://login.engie.nl"
OKTA_ISSUER = f"{OKTA_ORG_URL}/oauth2/default"
OKTA_AUTHORIZE_URL = f"{OKTA_ISSUER}/v1/authorize"
OKTA_TOKEN_URL = f"{OKTA_ISSUER}/v1/token"
OKTA_AUTHN_URL = f"{OKTA_ORG_URL}/api/v1/authn"

# The app's public OIDC client. A public client has no secret; PKCE protects
# the code exchange. Recovered from nl.engie.BuildConfig.
OKTA_CLIENT_ID = "0oalrmez06eyFoFyh417"
OKTA_REDIRECT_URI = "engie://login/okta/callback"
OKTA_SCOPE = (
    "openid email profile offline_access "
    "okta.myAccount.password.manage okta.myAccount.password.read"
)

# Okta access tokens are short-lived; refresh this many seconds before expiry
# so a request never leaves with a token that dies in flight.
TOKEN_REFRESH_MARGIN = 60

DEFAULT_TIMEOUT = 30
