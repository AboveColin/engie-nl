# engie-nl

Async Python client for the private API behind the **ENGIE Energie NL** app
(`nl.engie.engieapp`). It reads what the app reads: your customer record and
EANs, daily consumption per meter, meter readings, the termijnbedrag advice,
invoices and payments, the smart-meter data mandate, outages, and the day-ahead
prices of ENGIE's dynamic contract.

ENGIE does not document or support this API. It can change without notice.
The map it is built from, with the receipts, lives in
`apk-reverse-engineering/docs/engie-nl/ENGIE_NL_API.md`.

## How the login works

The app logs in through Okta (`login.engie.nl`) with a browser PKCE flow and
sends the Okta access token straight to the gateway as `Authorization: Bearer`.
This package does the same without a browser: username and password go to
Okta's Authn API, the resulting session token completes the PKCE authorization,
and the token pair comes back. Only the token pair is kept. Accounts with a
second factor use the browser flow once and refresh from then on.

```python
import asyncio
from engie_nl import EngieClient, OktaAuth

async def main():
    async with OktaAuth() as auth:
        tokens = await auth.login("you@example.com", "password")
        async with EngieClient(tokens, auth=auth) as client:
            user = await client.get_user()
            for series in await client.get_consumptions(user.eans, days=7):
                for day in series.data:
                    print(series.ean, day.day, day.total, "kWh/m3")

asyncio.run(main())
```

Pass `on_tokens_updated=` to be told when the pair is refreshed, and persist
`TokenSet.to_dict()`. Home Assistant passes its own `aiohttp` session via
`session=`.

## What is read-only

Everything in this package. The gateway also has endpoints that change your
contract, meter readings, prepayment and payment details. They are documented
in the API map and deliberately not implemented here.

## Scripts

- `scripts/login.py`: interactive login, stores the token pair at
  `~/.config/engie-nl/tokens.json` (mode 0600). `--browser` for MFA accounts.
- `scripts/probe.py`: reads every supported endpoint once and writes the raw
  responses to `tests/fixtures/_live/` (gitignored) for inspection.

## Development

```sh
uv venv .venv && uv pip install -e '.[dev]'
.venv/bin/pytest
.venv/bin/pylint engie_nl
```

Tests run the client against a loopback aiohttp server that plays both Okta
and the gateway; no network, no mocks of aiohttp internals.
