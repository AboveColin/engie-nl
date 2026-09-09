"""engie-nl: async client for the private API behind the ENGIE Energie NL app."""

from .auth import BrowserLogin, EmailChallenge, OktaAuth, TokenSet, make_pkce_pair
from .client import EngieClient
from .exceptions import (
    EngieApiError,
    EngieAuthError,
    EngieEmailCodeRequired,
    EngieError,
    EngieMfaRequiredError,
    EngieNetworkError,
    EngieRateLimited,
    EngieWriteBlocked,
)
from .net2grid import Net2GridClient, P1Client
from .models import (
    Consumption,
    ConsumptionSeries,
    DayAheadPrice,
    DeliveryAddress,
    DocumentRef,
    EnergyType,
    EstimationCosts,
    Mandate,
    MerPeriod,
    MeteringPoint,
    MeterReadings,
    OutageMessage,
    ProductInfo,
    Reading,
    Register,
    Tariffs,
    Transaction,
    TransactionStatus,
    User,
)

# The 180 dataclasses generated from the APK's api-map.json are not re-exported
# one by one: import them from engie_nl.generated. The 19 below are the curated
# ones, which carry behaviour the generator cannot infer.
from . import generated  # noqa: E402  pylint: disable=wrong-import-position

__version__ = "0.2.1"

__all__ = [
    "__version__",
    "generated",
    "BrowserLogin",
    "EmailChallenge",
    "OktaAuth",
    "TokenSet",
    "make_pkce_pair",
    "EngieClient",
    "EngieApiError",
    "EngieAuthError",
    "EngieEmailCodeRequired",
    "EngieError",
    "EngieMfaRequiredError",
    "EngieNetworkError",
    "EngieRateLimited",
    "EngieWriteBlocked",
    "Net2GridClient",
    "P1Client",
    "Consumption",
    "ConsumptionSeries",
    "DayAheadPrice",
    "DeliveryAddress",
    "DocumentRef",
    "EnergyType",
    "EstimationCosts",
    "Mandate",
    "MerPeriod",
    "MeteringPoint",
    "MeterReadings",
    "OutageMessage",
    "ProductInfo",
    "Reading",
    "Register",
    "Tariffs",
    "Transaction",
    "TransactionStatus",
    "User",
]
