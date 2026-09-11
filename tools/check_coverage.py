#!/usr/bin/env python3
"""Check that every mapped endpoint has a method, and every method a mapping.

Two failures this catches. A path in the APK that nothing in the package calls
means the surface is not complete. A path in the package that the APK does not
declare means a typo, and a typo in a URL is a 404 nobody sees until runtime.

Run it as part of the test suite (tests/test_coverage.py) or on its own:

    python3 tools/check_coverage.py
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = REPO / "engie_nl"

# The map is extracted by a separate repo that is not published with this one.
# Point ENGIE_NL_API_MAP at its api-map.json; the fallback is a checkout sitting
# beside this one. The tests skip themselves when neither resolves.
DEFAULT_MAP = Path(
    os.environ.get("ENGIE_NL_API_MAP")
    or REPO.parent / "apk-reverse-engineering/docs/engie-nl/api-map.json"
)

# Endpoints the package deliberately does not call, with the reason. Empty
# today: every mapped endpoint has a method.
EXCLUDED: dict[tuple[str, str], str] = {}

# A path with an f-string placeholder in the source, mapped back to the {name}
# form the APK declares. Matching is on shape, not on the placeholder's name.
PLACEHOLDER = re.compile(r"\{[^}]*\}")


def normalise(path: str) -> str:
    """Compare paths by shape: leading slash and placeholder names do not matter."""
    return PLACEHOLDER.sub("{}", path.strip()).lstrip("/")


def mapped_endpoints(map_path: Path) -> dict[tuple[str, str], str]:
    """Every verb+path the APK declares, keyed by (verb, normalised path)."""
    endpoints = json.loads(map_path.read_text())["endpoints"]
    return {(e["verb"], normalise(e["path"])): e["path"] for e in endpoints}


def path_constants() -> dict[str, str]:
    """The ``PATH_*`` values in constants.py, so a name resolves to its path.

    The core reads on EngieClient use these rather than literals. Without this
    the checker reports ten covered endpoints as missing.
    """
    tree = ast.parse((PACKAGE / "constants.py").read_text())
    out: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str) and target.id.startswith("PATH_"):
                out[target.id] = node.value.value
    return out


def called_endpoints() -> dict[tuple[str, str], list[str]]:
    """Every verb+path the package sends, found by walking the AST.

    Reading the source rather than importing it keeps this honest: a method that
    builds its path in a way the checker cannot see shows up as uncovered rather
    than silently passing.
    """
    found: dict[tuple[str, str], list[str]] = {}
    constants = path_constants()

    def record(verb: str, path: str, where: str) -> None:
        found.setdefault((verb.upper(), normalise(path)), []).append(where)

    def literal(node: ast.expr) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name) and node.id in constants:
            return constants[node.id]
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in constants
        ):
            return constants[node.func.value.id]
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                else:
                    parts.append("{}")
            return "".join(parts)
        return None

    for source in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(source.read_text())
        where = str(source.relative_to(REPO))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            name = node.func.attr
            if name in {"_get", "get"} and node.args and name == "_get":
                path = literal(node.args[0])
                if path:
                    record("GET", path, where)
            elif name in {"_write", "_query", "_request"} and len(node.args) >= 2:
                verb = literal(node.args[0])
                path = literal(node.args[1])
                if verb and path and verb.isupper():
                    record(verb, path, where)
    return found


def main() -> int:
    map_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAP
    if not map_path.exists():
        print(f"api-map.json not found at {map_path}", file=sys.stderr)
        return 1

    mapped = mapped_endpoints(map_path)
    called = called_endpoints()

    missing = sorted(key for key in mapped if key not in called and key not in EXCLUDED)
    unknown = sorted(key for key in called if key not in mapped)

    print(f"{len(mapped)} endpoints in the map, {len(called)} reachable from the package")
    if EXCLUDED:
        print(f"{len(EXCLUDED)} deliberately excluded:")
        for key, why in EXCLUDED.items():
            print(f"  {key[0]:6s} {key[1]}  ({why})")
    if missing:
        print(f"\n{len(missing)} mapped endpoints have no method:")
        for verb, path in missing:
            print(f"  {verb:6s} {path}")
    if unknown:
        print(f"\n{len(unknown)} paths are called but not in the map (typo?):")
        for verb, path in unknown:
            print(f"  {verb:6s} {path}  <- {', '.join(sorted(set(called[(verb, path)])))}")
    if not missing and not unknown:
        print("\nevery mapped endpoint has a method, and every called path is mapped")
    return 1 if (missing or unknown) else 0


if __name__ == "__main__":
    raise SystemExit(main())
