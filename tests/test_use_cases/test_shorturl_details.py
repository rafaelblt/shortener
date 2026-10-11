import pytest

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import UUID

from shortener.domain import (
    ShortURL,
    ShortURLID,
    ShortURLStatus,
    Slug,
    TargetURL,
    UserID,
)
from shortener.use_cases.shorturl_details import ShortURLDetails


ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a11")
OWNER_ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
CREATED_AT = datetime(2002, 2, 2, tzinfo=timezone.utc)
LAST_RESOLVED_AT = datetime(2004, 4, 4, tzinfo=timezone.utc)


def restore(last_resolved_at: datetime | None) -> ShortURL:
    return ShortURL.restore(
        id=ShortURLID(ID),
        slug=Slug("my-slug"),
        target_url=TargetURL("https://example.com"),
        owner_id=UserID(OWNER_ID),
        status=ShortURLStatus.DEACTIVATED,
        resolution_count=5,
        created_at=CREATED_AT,
        last_resolved_at=last_resolved_at,
    )


@pytest.mark.parametrize(
    "last_resolved_at",
    [
        pytest.param(LAST_RESOLVED_AT, id="resolved"),
        pytest.param(None, id="never resolved"),
    ],
)
def test_from_entity_keeps_the_values_of_the_shorturl(
    last_resolved_at: datetime | None,
):
    assert ShortURLDetails.from_entity(restore(last_resolved_at)) == ShortURLDetails(
        id=ID,
        slug="my-slug",
        target_url="https://example.com",
        owner_id=OWNER_ID,
        status="deactivated",
        resolution_count=5,
        created_at=CREATED_AT,
        last_resolved_at=last_resolved_at,
    )


def test_from_entity_only_holds_primitives():
    details = ShortURLDetails.from_entity(restore(LAST_RESOLVED_AT))
    assert {field: type(value) for field, value in vars(details).items()} == {
        "id": UUID,
        "slug": str,
        "target_url": str,
        "owner_id": UUID,
        "status": str,
        "resolution_count": int,
        "created_at": datetime,
        "last_resolved_at": datetime,
    }


def test_is_immutable():
    details = ShortURLDetails.from_entity(restore(LAST_RESOLVED_AT))
    with pytest.raises(FrozenInstanceError):
        details.slug = "other-slug"  # type: ignore
