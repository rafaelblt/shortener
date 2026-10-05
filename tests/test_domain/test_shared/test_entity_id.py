import pytest

from dataclasses import FrozenInstanceError
from uuid import UUID

from shortener.domain.shared.entity_id import EntityID


VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
OTHER_VALUE = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11")


def test_keeps_the_value():
    assert EntityID(VALUE).value == VALUE


@pytest.mark.parametrize("value", [str(VALUE), VALUE.int, None])
def test_rejects_a_value_that_is_not_a_uuid(value):
    with pytest.raises(
        TypeError, match="The EntityID value must be an instance of UUID"
    ):
        EntityID(value)


def test_is_equal_to_an_id_with_the_same_value():
    assert EntityID(VALUE) == EntityID(VALUE)


def test_is_not_equal_to_an_id_with_another_value():
    assert EntityID(VALUE) != EntityID(OTHER_VALUE)


def test_has_the_same_hash_as_an_id_with_the_same_value():
    assert hash(EntityID(VALUE)) == hash(EntityID(VALUE))


def test_is_immutable():
    entity_id = EntityID(VALUE)
    with pytest.raises(FrozenInstanceError):
        entity_id.value = OTHER_VALUE  # type: ignore


def test_str_is_the_uuid_string():
    assert str(EntityID(VALUE)) == "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"
