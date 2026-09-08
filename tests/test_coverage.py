"""The package covers every endpoint the APK declares, and invents none.

This is the test that keeps "fully mapped" true. It reads the same api-map.json
the models are generated from, so a new APK that adds an endpoint fails here
before anything else notices.

Skipped when the map is not checked out: the map lives in a separate repo, and a
missing sibling directory is not a defect in this package.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import check_coverage  # noqa: E402  pylint: disable=wrong-import-position


pytestmark = pytest.mark.skipif(
    not check_coverage.DEFAULT_MAP.exists(),
    reason=f"api-map.json not checked out at {check_coverage.DEFAULT_MAP}",
)


def test_every_mapped_endpoint_has_a_method() -> None:
    mapped = check_coverage.mapped_endpoints(check_coverage.DEFAULT_MAP)
    called = check_coverage.called_endpoints()
    missing = sorted(k for k in mapped if k not in called and k not in check_coverage.EXCLUDED)
    assert not missing, f"{len(missing)} endpoints have no method: {missing}"


def test_no_method_calls_an_unmapped_path() -> None:
    """A path the APK does not declare is a typo, and a typo in a URL is a 404."""
    mapped = check_coverage.mapped_endpoints(check_coverage.DEFAULT_MAP)
    called = check_coverage.called_endpoints()
    unknown = sorted(k for k in called if k not in mapped)
    assert not unknown, f"{len(unknown)} paths are not in the map: {unknown}"
