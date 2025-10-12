import pytest

from datetime import timedelta

from shortener.domain.shared.valueobjects import URL
from shortener.domain.shared.email import Email
from shortener.infra.settings import converters


def test_str_to_timedelta_valid():
    value = "1"
    retrieved = converters.str_minutes_to_timedelta(value)
    assert isinstance(retrieved, timedelta)
    assert retrieved.seconds / 60 == int(value)


def test_str_to_timedelta_invalid():
    value = "1.2"
    with pytest.raises(converters.ConversionError) as error:
        converters.str_minutes_to_timedelta(value)
    assert value in error.value.__str__()


def test_str_to_email_valid():
    value = "example@gmail.com"
    retrieved = converters.str_to_email(value)
    assert isinstance(retrieved, Email)
    assert retrieved == value


def test_str_to_email_invalid():
    value = "example@com"
    with pytest.raises(converters.ConversionError) as error:
        converters.str_to_email(value)
    assert value in error.value.__str__()


def test_str_to_url_valid():
    value = "http://example.com"
    retrieved = converters.str_to_url(value)
    assert isinstance(retrieved, URL)
    assert retrieved == value


def test_str_to_url_invalid():
    value = "http://"
    with pytest.raises(converters.ConversionError) as error:
        converters.str_to_url(value)
    assert value in error.value.__str__()
