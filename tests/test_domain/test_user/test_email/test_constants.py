import re
from shortener.domain.user.fields.email import EMAIL_REGEX_PATTERN


def test_email_regex_pattern():
    assert isinstance(EMAIL_REGEX_PATTERN, re.Pattern)
    assert EMAIL_REGEX_PATTERN.pattern == r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
