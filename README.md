# engie-nl

Async Python client for the private API behind the **ENGIE Energie NL** app
(`nl.engie.engieapp`). It covers the whole thing: all 148 endpoints the app
declares, with 199 typed models.

The reads a household actually polls are on the client itself: the customer
record and EANs, daily consumption per meter, meter readings, the termijnbedrag
advice, invoices, the smart-meter data mandate, outages, and day-ahead prices.
The rest is grouped by area, `client.tariffs`, `client.assets`, `client.enode`
and so on, listed below.

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

## The whole surface

| Group | What it covers |
|---|---|
| `client.get_*` | user, consumptions, meterstands, estimations, transactions, documents, mandates, outages, day-ahead prices, MER periods, opening hours |
| `client.tariffs` | the contract's own rates, `GET /api/v1/tariffs` |
| `client.meter` | filing and withdrawing meter readings, the P4 feed, dongle activation |
| `client.billing` | invoice payment status, documents, the MER report, the termijnbedrag, iDEAL |
| `client.account` | profile, settings cards, areas of interest, passwords, payment details |
| `client.mandates` | granting and withdrawing the smart-meter mandate |
| `client.assets` | declared solar panels, heat pumps, batteries, cars, chargers, aircos |
| `client.enode` | linked vehicles and chargers, locations, charge policies, sessions |
| `client.smart_charging` | ENGIE's own smart-charging programme |
| `client.happy_hour` | announced Happy Hours, subscriptions, payouts |
| `client.solar` | solar potential, quotes, home and energy scans |
| `client.address` | postcode lookup, iDIN verification, moving the contract |
| `client.support` | opening hours, waiting time, advice articles, feedback, chat |
| `client.ev` | charge card and charging station lead forms |
| `client.legacy` | pre-Okta authentication and account creation |
| `Net2GridClient` | the P1 dongle, on Net2Grid's own host |

`tools/check_coverage.py` compares the package against the APK map and is run by
the test suite, so "all 148" stays true rather than being a claim in a README.

## Writes are off unless you ask

Every method that changes the account raises `EngieWriteBlocked` on a normal
client. The endpoints behind them are not test fixtures: `POST
/api/v1/meterstands` files a meter reading with the supplier who bills you, `PUT
/api/v1/prepayment` changes a direct debit, and `POST /api/v1/contract/move`
moves the contract to another address.

```python
async with EngieClient(tokens, auth=auth, allow_writes=True) as client:
    await client.billing.set_prepayment(user.eans, amount=195)
```

Two POSTs are queries despite the verb, `/api/v1/readings` and
`/api/v1/p4-errors`, and need no permission: both send a body to read P4 data
back.

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
.venv/bin/pytest --cov          # line and branch coverage, gated at 100%
.venv/bin/pylint engie_nl
.venv/bin/mypy engie_nl
```

Tests run the client against a loopback aiohttp server that plays both Okta
and the gateway; no network, no mocks of aiohttp internals.

`--cov` needs no other flags: the source list, branch coverage and the 100%
gate are in `pyproject.toml`, so the number is the same wherever it is run.
Every value in the tests is invented. Nothing in `tests/` came from a real
account; `scripts/probe.py` writes real responses to the gitignored
`tests/fixtures/_live/` and no test reads them.
