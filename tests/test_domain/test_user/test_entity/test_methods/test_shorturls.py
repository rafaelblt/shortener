import pytest

from shortener.domain.user import User
from shortener.domain.user.exceptions import UserShortURLLimitReachedError


@pytest.mark.asyncio
async def test_get_shorturls(poor_user: User):
    retrieved = await poor_user.get_shorturls()
    assert retrieved == []


@pytest.mark.asyncio
async def test_add_shorturl(poor_user: User, normal_shorturl):
    await poor_user.add_shorturl(normal_shorturl)
    assert await poor_user.get_shorturls() == [normal_shorturl]


@pytest.mark.asyncio
async def test_add_shorturls_raises_limit_reached(poor_user: User, normal_shorturl, other_shorturl):
    poor_user.plan._max_shorturls = 1
    await poor_user.add_shorturl(normal_shorturl)
    with pytest.raises(UserShortURLLimitReachedError) as error:
        await poor_user.add_shorturl(other_shorturl)
    assert error.value.max_shorturls == 1
