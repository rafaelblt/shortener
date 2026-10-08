import pytest

from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from uuid import UUID

from shortener.domain.shorturl import (
    ShortURL,
    ShortURLID,
    ShortURLStatus,
    OwnerID,
    Slug,
    TargetURL,
)
from shortener.domain.shorturl.exceptions import ShortURLDeactivatedError
from tests.utils.text_helpers import assert_mentions


CHANGES = [
    pytest.param(ShortURL.change_slug, "slug", Slug("new-slug"), id="slug"),
    pytest.param(
        ShortURL.change_target_url,
        "target_url",
        TargetURL("https://new.example.com"),
        id="target_url",
    ),
]


@pytest.fixture
def fields(owner_id: OwnerID) -> dict[str, Any]:
    # status, resolution_count and last_resolved_at differ from what create()
    # sets, so the tests can tell that restore() keeps them.
    return {
        "id": ShortURLID(UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11")),
        "slug": Slug("i-am-slug"),
        "target_url": TargetURL("https://google.com"),
        "owner_id": owner_id,
        "status": ShortURLStatus.DEACTIVATED,
        "resolution_count": 5,
        "created_at": datetime(2002, 2, 2, tzinfo=timezone.utc),
        "last_resolved_at": datetime(2004, 4, 4, tzinfo=timezone.utc),
    }


@pytest.fixture
def deactivated_shorturl(fields: dict[str, Any]) -> ShortURL:
    return ShortURL.restore(**{**fields, "status": ShortURLStatus.DEACTIVATED})


def test_create_keeps_the_given_values(owner_id: OwnerID, now: datetime):
    slug = Slug("my-slug")
    target_url = TargetURL("https://example.com")

    shorturl = ShortURL.create(
        slug=slug, target_url=target_url, owner_id=owner_id, now=now
    )

    assert shorturl.slug == slug
    assert shorturl.target_url == target_url
    assert shorturl.owner_id == owner_id
    assert shorturl.created_at == now


def test_create_starts_active_with_no_resolutions(normal_shorturl: ShortURL):
    assert normal_shorturl.status == ShortURLStatus.ACTIVE
    assert normal_shorturl.resolution_count == 0
    assert normal_shorturl.last_resolved_at is None


def test_create_generates_a_new_id_each_time(
    normal_shorturl: ShortURL, other_shorturl: ShortURL
):
    assert normal_shorturl.id != other_shorturl.id


def test_restore_keeps_the_given_values(fields: dict[str, Any]):
    shorturl = ShortURL.restore(**fields)
    assert {name: getattr(shorturl, name) for name in fields} == fields


def test_restore_keeps_datetimes_in_any_timezone(fields: dict[str, Any]):
    utc_minus_3 = datetime(2002, 2, 2, tzinfo=timezone(timedelta(hours=-3)))
    naive = datetime(2006, 6, 6)

    shorturl = ShortURL.restore(
        **{**fields, "created_at": utc_minus_3, "last_resolved_at": naive}
    )

    assert shorturl.created_at == utc_minus_3
    # Aware datetimes are equal when they are the same moment, in any timezone.
    assert shorturl.created_at.tzinfo == utc_minus_3.tzinfo
    assert shorturl.last_resolved_at == naive


@pytest.mark.parametrize(
    "field, value",
    [
        ("id", 1),
        ("slug", "my-slug"),
        ("target_url", "https://github.com"),
        ("owner_id", 1),
        ("status", "active"),
        ("resolution_count", "1"),
        ("created_at", 1992),
        ("created_at", None),
        ("last_resolved_at", 1992),
    ],
)
def test_restore_rejects_a_field_of_the_wrong_type(
    fields: dict[str, Any], field: str, value: object
):
    with pytest.raises(TypeError) as raised:
        ShortURL.restore(**{**fields, field: value})
    expected_type = type(fields[field])
    assert_mentions(
        str(raised.value), field, expected_type.__name__, type(value).__name__
    )


def test_restore_rejects_a_negative_resolution_count(fields: dict[str, Any]):
    resolution_count = -1
    with pytest.raises(ValueError) as raised:
        ShortURL.restore(**{**fields, "resolution_count": resolution_count})
    assert_mentions(str(raised.value), "resolution_count", str(resolution_count))


def test_restore_takes_keyword_arguments_only(fields: dict[str, Any]):
    with pytest.raises(TypeError):
        ShortURL.restore(*fields.values()) # type: ignore


@pytest.mark.parametrize("change, field, new_value", CHANGES)
def test_change_replaces_the_field(
    normal_shorturl: ShortURL,
    change: Callable[[ShortURL, Any], None],
    field: str,
    new_value: str,
):
    change(normal_shorturl, new_value)
    assert getattr(normal_shorturl, field) == new_value


@pytest.mark.parametrize("change, field, new_value", CHANGES)
def test_change_rejects_a_value_of_another_type(
    normal_shorturl: ShortURL,
    change: Callable[[ShortURL, Any], None],
    field: str,
    new_value: str,
):
    with pytest.raises(TypeError) as raised:
        change(normal_shorturl, "a plain str")
    assert_mentions(
        str(raised.value), field, type(new_value).__name__, str.__name__
    )


def test_resolve_returns_the_target_url(normal_shorturl: ShortURL, now: datetime):
    assert normal_shorturl.resolve(now) == normal_shorturl.target_url


def test_resolve_adds_one_to_the_resolution_count_on_each_call(
    normal_shorturl: ShortURL, now: datetime
):
    normal_shorturl.resolve(now)
    normal_shorturl.resolve(now)
    assert normal_shorturl.resolution_count == 2


def test_resolve_sets_last_resolved_at_to_now(normal_shorturl: ShortURL, now: datetime):
    normal_shorturl.resolve(now)
    assert normal_shorturl.last_resolved_at == now


def test_resolve_accepts_a_naive_now(normal_shorturl: ShortURL):
    naive = datetime(2026, 1, 1)
    normal_shorturl.resolve(naive)
    assert normal_shorturl.last_resolved_at == naive


def test_resolve_rejects_a_now_that_is_not_a_datetime(normal_shorturl: ShortURL):
    with pytest.raises(TypeError) as raised:
        normal_shorturl.resolve(None) # type: ignore
    assert_mentions(str(raised.value), "now", datetime.__name__, type(None).__name__)


def test_resolve_checks_now_before_the_status(deactivated_shorturl: ShortURL):
    with pytest.raises(TypeError):
        deactivated_shorturl.resolve(None) # type: ignore


def test_resolve_of_a_deactivated_shorturl_raises_and_counts_nothing(
    deactivated_shorturl: ShortURL, now: datetime
):
    resolution_count = deactivated_shorturl.resolution_count
    last_resolved_at = deactivated_shorturl.last_resolved_at

    with pytest.raises(ShortURLDeactivatedError):
        deactivated_shorturl.resolve(now)

    assert deactivated_shorturl.resolution_count == resolution_count
    assert deactivated_shorturl.last_resolved_at == last_resolved_at


@pytest.mark.parametrize("status", ShortURLStatus)
def test_enable_makes_a_shorturl_in_any_status_active(
    fields: dict[str, Any], status: ShortURLStatus
):
    shorturl = ShortURL.restore(**{**fields, "status": status})
    shorturl.enable()
    assert shorturl.status == ShortURLStatus.ACTIVE


@pytest.mark.parametrize("status", ShortURLStatus)
def test_disable_makes_a_shorturl_in_any_status_deactivated(
    fields: dict[str, Any], status: ShortURLStatus
):
    shorturl = ShortURL.restore(**{**fields, "status": status})
    shorturl.disable()
    assert shorturl.status == ShortURLStatus.DEACTIVATED
