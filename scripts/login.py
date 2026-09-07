#!/usr/bin/env python3
"""Log in to ENGIE once and store the Okta token pair, never the password.

Run it yourself; it prompts. Tokens land in ``~/.config/engie-nl/tokens.json``
with mode 0600. ``scripts/probe.py`` and the Home Assistant config flow read
that file.

    python scripts/login.py                 # email/password, then the code ENGIE mails you
    python scripts/login.py --browser       # MFA accounts: open a URL, paste the callback
    python scripts/login.py --try-password-grant   # experiment, records the answer

Every outcome, including a refusal, is a receipt for the API map. The script
prints what Okta answered without printing any token.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engie_nl import (  # noqa: E402
    EngieAuthError,
    EngieEmailCodeRequired,
    EngieMfaRequiredError,
    OktaAuth,
    TokenSet,
)

TOKEN_FILE = Path(os.environ.get("ENGIE_TOKENS", Path.home() / ".config" / "engie-nl" / "tokens.json"))


def save(tokens: TokenSet) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tokens.to_dict(), indent=2), encoding="utf-8")
    TOKEN_FILE.chmod(0o600)
    print(f"stored token pair in {TOKEN_FILE} (mode 0600)")
    print(f"  access token: {len(tokens.access_token)} chars, expires in {int(tokens.expires_at - __import__('time').time())} s")
    print(f"  refresh token: {'yes' if tokens.refresh_token else 'NO, sessions will not survive an hour'}")


async def login_with_code(auth: OktaAuth, username: str, password: str) -> TokenSet:
    """Log in, prompting for the one-time code when ENGIE asks for one.

    This account does ask, every time, so the refresh token in the saved pair is
    what keeps later runs from needing the mailbox again.
    """
    try:
        return await auth.login(username, password)
    except EngieEmailCodeRequired as err:
        print("\nENGIE emailed a one-time code. It expires in a few minutes.")
        code = input("code from the email: ").strip()
        return await auth.submit_email_code(err.challenge, code)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--browser", action="store_true", help="browser PKCE flow (works with MFA)")
    parser.add_argument("--try-password-grant", action="store_true", help="try the ROPC grant first and report")
    parser.add_argument("--check", action="store_true", help="run the real login and report the outcome without saving the tokens")
    args = parser.parse_args()

    async with OktaAuth() as auth:
        if args.browser:
            started = auth.begin_browser_login()
            print("Open this URL, log in, and copy the engie://login/okta/callback?... URL the browser fails to open:\n")
            print(started.url, "\n")
            callback = input("callback URL (or bare code): ").strip()
            tokens = await auth.finish_browser_login(callback, started)
            save(tokens)
            return 0

        username = input("Mijn ENGIE username (email): ").strip()
        password = getpass.getpass("password: ")

        if args.check:
            # Runs the real login and throws the tokens away, so a refusal is
            # Okta's own words about this account rather than a guess.
            try:
                tokens = await login_with_code(auth, username, password)
            except EngieMfaRequiredError as err:
                print(f"login: Okta wants another authenticator ({err.status})")
                print(f"  offered: {[f.get('factorType') for f in err.factors]}")
                print("  use: python scripts/login.py --browser")
                return 2
            except EngieAuthError as err:
                print(f"login: REFUSED. {err}")
                return 1
            print(f"login: accepted, access token is {len(tokens.access_token)} chars, not saved")
            return 0

        if args.try_password_grant:
            try:
                tokens = await auth.password_grant(username, password)
            except EngieAuthError as err:
                print(f"password grant: REFUSED ({err})")
            else:
                print("password grant: ACCEPTED by the mobile client")
                save(tokens)
                return 0

        try:
            tokens = await login_with_code(auth, username, password)
        except EngieMfaRequiredError as err:
            print(f"Okta wants a second factor ({err.status}); factors: {[f.get('factorType') for f in err.factors]}")
            print("rerun with --browser")
            return 2
        except EngieAuthError as err:
            print(f"login failed: {err}")
            return 1
        save(tokens)
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
