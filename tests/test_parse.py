"""Turning a decoded response into models, including the shapes that are not one."""

from __future__ import annotations

import pytest

from engie_nl._parse import as_dicts, eans_param, parse_list, parse_one

EAN_E = "871694840000000001"
EAN_G = "871694840000000002"


def test_eans_param_is_one_key_per_value() -> None:
    """A comma-joined string is rejected by the gateway, so never build one."""
    assert eans_param(EAN_E) == [("eans[]", EAN_E)]
    assert eans_param([EAN_E, EAN_G]) == [("eans[]", EAN_E), ("eans[]", EAN_G)]
    assert eans_param(iter([EAN_E])) == [("eans[]", EAN_E)]


def test_eans_param_refuses_an_empty_list() -> None:
    """Without an EAN the gateway answers for nobody; fail here instead."""
    with pytest.raises(ValueError, match="at least one EAN"):
        eans_param([])


def test_as_dicts_unwraps_both_list_shapes() -> None:
    """A bare list, a {"data": [...]} envelope, and anything else."""
    assert as_dicts([{"a": 1}, "not a dict", {"b": 2}]) == [{"a": 1}, {"b": 2}]
    assert as_dicts({"data": [{"a": 1}, 7]}) == [{"a": 1}]
    assert as_dicts({"data": "not a list"}) == []
    assert as_dicts({"other": [{"a": 1}]}) == []
    assert as_dicts("Service Unavailable") == []
    assert as_dicts(None) == []


def test_parse_list_and_parse_one() -> None:
    assert parse_list([{"n": 1}, {"n": 2}], lambda d: d["n"]) == [1, 2]
    assert parse_list("not a list", lambda d: d["n"]) == []
    assert parse_one({"n": 3}, lambda d: d["n"]) == 3
    assert parse_one([{"n": 3}], lambda d: d["n"]) is None
    assert parse_one(None, lambda d: d["n"]) is None
