"""The 180 generated dataclasses, tested by the one rule the generator promises.

``generated.py`` says every field is optional, because the gateway omits keys
freely and a missing key must not raise. That is a single invariant over 180
classes, so it is checked as one, in a loop, rather than hand-written 180 times.
The loop is not a formality: it calls the real ``from_api`` of every class with
an empty body, with a body of unknown keys, and with a wrong type in every
declared field, and each of those is a way the live gateway has already been
seen to answer.

Nothing here asserts a field name. The names come from the same api-map.json
the classes are generated from, so asserting them would only restate the
generator's output. ``tests/test_coverage.py`` is what checks the map.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from engie_nl import generated
from engie_nl.generated import _obj


def _model_classes() -> list[Any]:
    """Every dataclass ``generated.py`` defines, excluding the ones it imports.

    ``Consumption``, ``Register``, ``Tariffs`` and ``Transaction`` are in the
    module's namespace but come from ``models.py``, where they are hand-written
    and carry behaviour. They are tested in ``test_models.py``.
    """
    found = [
        obj
        for name, obj in vars(generated).items()
        if isinstance(obj, type)
        and dataclasses.is_dataclass(obj)
        and obj.__module__ == generated.__name__
        and not name.startswith("_")
    ]
    assert len(found) > 150, f"expected the generated module's ~180 classes, found {len(found)}"
    return sorted(found, key=lambda c: c.__name__)


MODELS: list[Any] = _model_classes()


def test_an_empty_body_parses_into_defaults() -> None:
    """The gateway answers ``{}`` for a record it has nothing for."""
    wrong: list[str] = []
    for model in MODELS:
        parsed = model.from_api({})
        assert isinstance(parsed, model)
        assert parsed.raw == {}, model.__name__
        for field in dataclasses.fields(parsed):
            value = getattr(parsed, field.name)
            if field.name != "raw" and not (value is None or value == [] or value == {}):
                wrong.append(f"{model.__name__}.{field.name} = {value!r}")
    assert not wrong, f"{len(wrong)} fields are not optional: {wrong}"


def test_raw_keeps_a_key_the_map_did_not_know() -> None:
    """A field ENGIE adds after the APK was read must survive on ``raw``."""
    body: dict[str, Any] = {"a_key_no_model_declares": [1, 2, 3]}
    for model in MODELS:
        assert model.from_api(body).raw == body, model.__name__


def test_every_field_survives_a_value_of_the_wrong_type() -> None:
    """A key present with a shape no coercion expects must coerce, not raise.

    The key names are the field names, which is right for most of the generated
    classes and harmless for the rest: a key that maps to nothing is a key the
    model ignores, and the point of the call is that it returns at all.
    """
    for model in MODELS:
        body = {field.name: object() for field in dataclasses.fields(model) if field.name != "raw"}
        assert model.from_api(body).raw == body, model.__name__


def test_obj_takes_a_nested_object_and_refuses_anything_else() -> None:
    """The gateway sends ``null`` where the map declared an object."""
    assert _obj({"culture": "nl-NL"}, generated.AbstractBaseResponse.from_api) == (
        generated.AbstractBaseResponse.from_api({"culture": "nl-NL"})
    )
    assert _obj(None, generated.AbstractBaseResponse.from_api) is None
    assert _obj([], generated.AbstractBaseResponse.from_api) is None


def test_a_populated_body_reaches_the_fields_it_names() -> None:
    """One class read end to end, so the loop above is not the only evidence."""
    token = generated.AccessTokenResponse.from_api(
        {"access_token": "gateway-access-0", "expires_in": "3600",
         "refresh_token": "gateway-refresh-0", "token_type": "Bearer"}
    )
    assert token.access_token == "gateway-access-0"
    assert token.expires_in == 3600  # the gateway sends it as a string
    assert token.refresh_token == "gateway-refresh-0"
    assert token.token_type == "Bearer"
