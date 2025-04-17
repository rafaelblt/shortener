import pytest

from shortener.domain.user.exceptions import (
    UserNameTooLongError, UserNameTooShortError, UserNameInvalidPatternError
)
from shortener.domain.user.fields.name import (
    Name, NAME_MAX_LENGTH, NAME_MIN_LENGTH
)


def test_validate_name():
    assert Name.validate_name("Lorenzo da Silva") == None


def test_validate_name_raises_user_name_too_long():
    value = "a" * (NAME_MAX_LENGTH + 1)
    with pytest.raises(
        UserNameTooLongError,
        match=f"Name must be at most {NAME_MAX_LENGTH} characters long."
    ):
        Name.validate_name(value)


def test_validate_name_raises_user_name_too_short():
    value = "a" * (NAME_MIN_LENGTH - 1)
    with pytest.raises(
        UserNameTooShortError,
        match=f"Name must be at least {NAME_MIN_LENGTH} characters long."
    ):
        Name.validate_name(value)


def test_validate_name_raises_user_name_invalid_pattern():
    value = "ħŋłđðßłħðßþħ°?þłħđ°?þħł?þŧħ°"
    with pytest.raises(
        UserNameInvalidPatternError,
        match=("Name must contain only letters, spaces, hyphens, "
               "and apostrophes.")
    ):
        Name.validate_name(value)
