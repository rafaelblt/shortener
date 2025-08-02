import pytest

from datetime import timedelta

from shortener.domain.shared.email import Email
from shortener.infra.settings import converters


def test_str_to_timedelta_valid():
    value = "1"
    retrieved = converters.convert_str_minutes_to_timedelta(value)
    assert isinstance(retrieved, timedelta)
    assert retrieved.seconds / 60 == int(value)


def test_str_to_timedelta_invalid():
    value = "1.2"
    with pytest.raises(converters.ConversionError) as error:
        converters.convert_str_minutes_to_timedelta(value)
    assert value in error.value.__str__()


def test_str_to_email_valid():
    value = "example@gmail.com"
    retrieved = converters.convert_str_to_email(value)
    assert isinstance(retrieved, Email)
    assert retrieved == value


def test_str_to_email_invalid():
    value = "example@com"
    with pytest.raises(converters.ConversionError) as error:
        converters.convert_str_to_email(value)
    assert value in error.value.__str__()
