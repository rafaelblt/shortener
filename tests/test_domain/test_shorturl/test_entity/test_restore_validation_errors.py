import pytest

from shortener.domain.shorturl import ShortURL


@pytest.fixture
def fields(normal_shorturl):
    return {
        "id": normal_shorturl.id,
        "slug": normal_shorturl.slug,
        "target_url": normal_shorturl.target_url,
        "owner_id": normal_shorturl.owner_id,
        "status": normal_shorturl.status,
        "visit_count": normal_shorturl.visit_count,
        "created_at": normal_shorturl.created_at,
        "expires_at": normal_shorturl.expires_at,
        "last_accessed_at": normal_shorturl.last_accessed_at,
    }


def get_type_error_message(attr, type_expected, got):
    return (
        f"The ShortURL {attr} must be an instance of {type_expected}, got "
        f"{type(got).__name__}"
    )


@pytest.mark.parametrize(
    "attr, type_expected, value",
    [
        ("id", "ShortURLID", 1),
        ("slug", "Slug", {"slug": "test-slug"}),
        ("target_url", "TargetURL", "https://github.com"),
        ("owner_id", "OwnerID", 1),
        ("status", "ShortURLStatus", "active"),
        ("visit_count", "int", "1"),
        ("created_at", "datetime", 1992),
        ("created_at", "datetime", None),
        ("expires_at", "datetime or None", 1992),
        ("last_accessed_at", "datetime or None", 1992),
    ],
)
def test_field_of_the_wrong_type_raises_type_error(fields: dict, attr, type_expected, value):
    e = get_type_error_message(attr=attr, type_expected=type_expected, got=value)
    with pytest.raises(TypeError, match=e):
        ShortURL.restore(**{**fields, attr: value})


def test_visit_count_lower_than_0_raises_value_error(fields: dict):
    visit_count = -1
    e = ("The ShortURL visit_count must be greater than or equal to 0, "
        f"got {visit_count}")
    with pytest.raises(ValueError, match=e):
        ShortURL.restore(**{**fields, "visit_count": visit_count})


def test_restore_takes_keyword_arguments_only(fields: dict):
    with pytest.raises(TypeError):
        ShortURL.restore(*fields.values()) # type: ignore
