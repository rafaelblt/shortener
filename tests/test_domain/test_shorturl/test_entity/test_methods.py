import pytest
from datetime import datetime

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl import ShortURLStatus
from shortener.domain.shorturl.exceptions import ShortURLDeactivatedError
from tests.utils.text_helpers import assert_mentions


def test_resolve_returns_the_target_url(normal_shorturl: ShortURL, now: datetime):
    assert normal_shorturl.resolve(now) == normal_shorturl.target_url


def test_resolve_increments_the_resolution_count(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.resolve(now)
    assert normal_shorturl.resolution_count == 1


def test_resolve_increments_the_resolution_count_on_each_call(
    normal_shorturl: ShortURL, now: datetime
):
    normal_shorturl.resolve(now)
    normal_shorturl.resolve(now)
    assert normal_shorturl.resolution_count == 2


def test_resolve_sets_last_resolved_at_to_now(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.resolve(now)
    assert normal_shorturl.last_resolved_at == now


def test_resolve_accepts_a_naive_datetime(normal_shorturl: ShortURL):
    naive = datetime(year=2026, month=1, day=1)
    normal_shorturl.resolve(naive)
    assert normal_shorturl.last_resolved_at == naive


def test_resolve_rejects_none(normal_shorturl: ShortURL):
    with pytest.raises(TypeError):
        normal_shorturl.resolve(None) # type: ignore


def test_resolve_type_error_names_the_now_parameter(normal_shorturl: ShortURL):
    with pytest.raises(TypeError) as raised:
        normal_shorturl.resolve(None) # type: ignore
    assert_mentions(str(raised.value), "now", datetime.__name__, type(None).__name__)


def test_resolve_rejects_none_before_checking_availability(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    with pytest.raises(TypeError):
        normal_shorturl.resolve(None) # type: ignore


def test_resolve_raises_deactivated_error(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.disable()
    with pytest.raises(ShortURLDeactivatedError):
        normal_shorturl.resolve(now)


def test_resolve_doesnt_count_the_resolution_when_deactivated(
    normal_shorturl: ShortURL, now: datetime
):
    normal_shorturl.disable()
    with pytest.raises(ShortURLDeactivatedError):
        normal_shorturl.resolve(now)
    assert normal_shorturl.resolution_count == 0
    assert normal_shorturl.last_resolved_at is None


def test_disable_deactivates_an_active_shorturl(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    assert normal_shorturl.status == ShortURLStatus.DEACTIVATED


def test_disable_keeps_a_deactivated_shorturl_deactivated(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    normal_shorturl.disable()
    assert normal_shorturl.status == ShortURLStatus.DEACTIVATED


def test_enable_activates_a_deactivated_shorturl(normal_shorturl: ShortURL):
    normal_shorturl.disable()
    normal_shorturl.enable()
    assert normal_shorturl.status == ShortURLStatus.ACTIVE


def test_enable_keeps_an_active_shorturl_active(normal_shorturl: ShortURL):
    normal_shorturl.enable()
    assert normal_shorturl.status == ShortURLStatus.ACTIVE

