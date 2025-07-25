from datetime import datetime


def assert_datetime(
    value: datetime, expected: datetime,
    year: bool = False,
    month: bool = False,
    day: bool = False,
    hour: bool = False,
    minute: bool = False,
    second: bool = False,
    microsecond: bool = False,
):
    assert isinstance(value, datetime)
    assert isinstance(expected, datetime)

    if year:
        assert value.year == expected.year
    if month:
        assert value.month == expected.month
    if day:
        assert value.day == expected.day
    if hour:
        assert value.hour == expected.hour
    if minute:
        assert value.minute == expected.minute
    if second:
        assert value.second == expected.second
    if microsecond:
        assert value.microsecond == expected.microsecond
