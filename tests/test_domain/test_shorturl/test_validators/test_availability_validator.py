import pytest

from datetime import datetime, timezone

from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.validators import AvailabilityValidator
from shortener.domain.shorturl.exceptions import (
    ShortURLInactiveError, ShortURLExpiredError
)


@pytest.fixture
def validator():
    return AvailabilityValidator()


@pytest.mark.asyncio
async def test_valid_shorturl(
    validator: AvailabilityValidator, normal_shorturl: ShortURL
):
    retrieved = await validator.validate(normal_shorturl)
    assert retrieved is None


@pytest.mark.asyncio
async def test_with_is_active_false(
    validator: AvailabilityValidator, normal_shorturl: ShortURL
):
    normal_shorturl.is_active = False
    with pytest.raises(ShortURLInactiveError, match="The ShortURL is not active"):
        await validator.validate(normal_shorturl)


@pytest.mark.asyncio
async def test_with_valid_expires_at(
    validator: AvailabilityValidator, normal_shorturl: ShortURL
):
    normal_shorturl.expires_at = datetime(
        year=3950, month=1, day=1, tzinfo=timezone.utc
    )
    await validator.validate(normal_shorturl)


@pytest.mark.asyncio
async def test_with_invalid_expires_at(
    validator: AvailabilityValidator, normal_shorturl: ShortURL
):
    normal_shorturl.expires_at = datetime(
        year=2020, month=1, day=1, tzinfo=timezone.utc
    )
    with pytest.raises(ShortURLExpiredError, match="The ShortURL has expired."):
        await validator.validate(normal_shorturl)
