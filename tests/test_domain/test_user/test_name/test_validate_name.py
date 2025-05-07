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
    with pytest.raises(
        NameTooLongError,
        match=f"Name must be at most {max_length} characters long. Got: {value}"
    ):
        Name.validate_name(value)


def test_validate_name_raises_name_too_short():
    min_length = NAME_MIN_LENGTH
    value = "a" * (min_length - 1)
    with pytest.raises(
        NameTooShortError,
        match=f"Name must be at least {min_length} characters long. Got: {value}"
    ):
        Name.validate_name(value)


def test_validate_name_raises_name_invalid_pattern():
    value = "ħŋłđðßłħðßþħ°?þłħđ°?þħł?þŧħ°"
    with pytest.raises(
        NameInvalidPatternError,
        match=re.escape(f"The name '{value}' does not match the required pattern.")
    ):
        Name.validate_name(value)
