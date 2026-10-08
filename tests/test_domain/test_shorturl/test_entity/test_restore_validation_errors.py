import pytest

from datetime import datetime

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl import (
    Slug, TargetURL, ShortURLStatus, ShortURLID, OwnerID
)
from tests.utils.text_helpers import assert_mentions


@pytest.fixture
def fields(normal_shorturl):
    return {
        "id": normal_shorturl.id,
        "slug": normal_shorturl.slug,
        "target_url": normal_shorturl.target_url,
        "owner_id": normal_shorturl.owner_id,
        "status": normal_shorturl.status,
        "resolution_count": normal_shorturl.resolution_count,
        "created_at": normal_shorturl.created_at,
        "last_resolved_at": normal_shorturl.last_resolved_at,
    }


@pytest.mark.parametrize(
    "attribute, expected_type, value",
    [
        ("id", ShortURLID, 1),
        ("slug", Slug, {"slug": "test-slug"}),
        ("target_url", TargetURL, "https://github.com"),
        ("owner_id", OwnerID, 1),
        ("status", ShortURLStatus, "active"),
        ("resolution_count", int, "1"),
        ("created_at", datetime, 1992),
        ("created_at", datetime, None),
        ("last_resolved_at", datetime, 1992),
    ],
)
def test_field_of_the_wrong_type_raises_type_error(
    fields: dict, attribute, expected_type, value
):
    with pytest.raises(TypeError) as raised:
        ShortURL.restore(**{**fields, attribute: value})
    assert_mentions(
        str(raised.value), attribute, expected_type.__name__, type(value).__name__
    )


def test_resolution_count_lower_than_0_raises_value_error(fields: dict):
    resolution_count = -1
    with pytest.raises(ValueError) as raised:
        ShortURL.restore(**{**fields, "resolution_count": resolution_count})
    assert_mentions(str(raised.value), "resolution_count", str(resolution_count))


def test_restore_takes_keyword_arguments_only(fields: dict):
    with pytest.raises(TypeError):
        ShortURL.restore(*fields.values()) # type: ignore
