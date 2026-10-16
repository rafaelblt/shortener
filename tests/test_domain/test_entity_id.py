from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest

from shortener.domain.entity_id import EntityID
from tests.utils.text_helpers import assert_mentions


VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
OTHER_VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11")


def test_keeps_the_value():
    assert EntityID(VALUE).value == VALUE


@pytest.mark.parametrize("value", [str(VALUE), VALUE.int, None])
def test_rejects_a_value_that_is_not_a_uuid(value: Any):
    with pytest.raises(TypeError) as raised:
        EntityID(value)
    assert_mentions(
        str(raised.value), EntityID.__name__, UUID.__name__, type(value).__name__
    )


def test_is_equal_only_to_an_id_with_the_same_value():
    assert EntityID(VALUE) == EntityID(VALUE)
    assert EntityID(VALUE) != EntityID(OTHER_VALUE)


def test_has_the_same_hash_as_an_id_with_the_same_value():
    assert hash(EntityID(VALUE)) == hash(EntityID(VALUE))


def test_is_immutable():
    entity_id = EntityID(VALUE)
    with pytest.raises(FrozenInstanceError):
        entity_id.value = OTHER_VALUE  # type: ignore[misc]


def test_str_is_the_uuid_string():
    assert str(EntityID(VALUE)) == str(VALUE)
