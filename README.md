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

The app logs in through Okta (`login.engie.nl`) and sends the Okta access token
straight to the gateway as `Authorization: Bearer`. ENGIE's org runs Okta
Identity Engine, so this package walks the interaction code flow: interact,
introspect, identify, then the password.

**ENGIE then emails a one-time code, and it is not optional.** `login()` asks
Okta to send the mail and raises `EngieEmailCodeRequired`; hand the code to
`submit_email_code()` to finish. Only the token pair is kept, never the
password. The scope includes `offline_access`, so this happens once: the
refresh token carries every later session without touching the mailbox.

```python
import asyncio
from engie_nl import EngieClient, EngieEmailCodeRequired, OktaAuth

async def main():
    async with OktaAuth() as auth:
        try:
            tokens = await auth.login("you@example.com", "password")
        except EngieEmailCodeRequired as err:
            code = input("code from the email: ")
            tokens = await auth.submit_email_code(err.challenge, code)

        async with EngieClient(tokens, auth=auth) as client:
            user = await client.get_user()
            for series in await client.get_consumptions(user.eans, days=7):
                for day in series.data:
                    print(series.ean, day.day, day.total, "kWh/m3")

asyncio.run(main())
```

Persist `tokens.to_dict()` and rebuild with `TokenSet.from_dict()`; losing the
refresh token means another trip to the mailbox.

Pass `on_tokens_updated=` to be told when the pair is refreshed, and persist
`TokenSet.to_dict()`. Home Assistant passes its own `aiohttp` session via
`session=`.

## What is read-only

Everything in this package. The gateway also has endpoints that change your
contract, meter readings, prepayment and payment details. They are documented
in the API map and deliberately not implemented here.

## Scripts

- `scripts/login.py`: interactive login. Prompts for the password, then for the
  code ENGIE emails, and stores the token pair at
  `~/.config/engie-nl/tokens.json` (mode 0600). `--check` runs the whole login
  and saves nothing; `--browser` uses the browser flow instead.
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
