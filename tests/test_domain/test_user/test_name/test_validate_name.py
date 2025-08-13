import pytest
import re

from shortener.domain.user.exceptions import (
    NameTooLongError, NameTooShortError, NameInvalidPatternError
)
from shortener.domain.user.fields.name import (
    Name, NAME_MAX_LENGTH, NAME_MIN_LENGTH
)


def test_validate_name():
    assert Name.validate_name("Lorenzo da Silva") == None


def test_validate_name_raises_name_too_long():
    max_length = NAME_MAX_LENGTH
    value = "a" * (max_length + 1)
    with pytest.raises(NameTooLongError) as error:
        Name.validate_name(value)
    assert error.value.value == value
    assert error.value.max_length == max_length


def test_validate_name_raises_name_too_short():
    min_length = NAME_MIN_LENGTH
    value = "a" * (min_length - 1)
    with pytest.raises(NameTooShortError) as error:
        Name.validate_name(value)
    assert error.value.value == value
    assert error.value.min_length == min_length


def test_validate_name_raises_name_invalid_pattern():
    value = "ħŋłđðßłħðßþħ°?þłħđ°?þħł?þŧħ°"
    with pytest.raises(NameInvalidPatternError) as error:
        Name.validate_name(value)
    assert error.value.value == value
