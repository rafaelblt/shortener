import re
from shortener.domain.user.fields.name import (
    NAME_MAX_LENGTH, NAME_MIN_LENGTH, NAME_REGEX_PATTERN
)


def test_name_max_length():
    assert NAME_MAX_LENGTH == 200


def test_name_min_length():
    assert NAME_MIN_LENGTH == 2


def test_name_regex_pattern():
    assert isinstance(NAME_REGEX_PATTERN, re.Pattern)
    assert NAME_REGEX_PATTERN.pattern == r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$"
