from datetime import datetime


def assert_datetime(
    actual: datetime, expected: datetime,
    year: bool = False,
    month: bool = False,
    day: bool = False,
    hour: bool = False,
    minute: bool = False,
    second: bool = False,
    microsecond: bool = False,
):
    assert isinstance(actual, datetime)
    assert isinstance(expected, datetime)

    if year:
        assert actual.year == expected.year
    if month:
        assert actual.month == expected.month
    if day:
        assert actual.day == expected.day
    if hour:
        assert actual.hour == expected.hour
    if minute:
        assert actual.minute == expected.minute
    if second:
        assert actual.second == expected.second
    if microsecond:
        assert actual.microsecond == expected.microsecond
