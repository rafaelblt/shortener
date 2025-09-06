import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User
from shortener.domain.user import exceptions


@pytest.mark.asyncio
async def test_get_shorturls(poor_user: User):
    retrieved = await poor_user.get_shorturls()
    assert retrieved == []


@pytest.mark.asyncio
async def test_add_shorturl(poor_user: User, normal_shorturl):
    await poor_user.add_shorturl(normal_shorturl)
    assert normal_shorturl.owner_pk == poor_user.pk
    assert await poor_user.get_shorturls() == [normal_shorturl]


@pytest.mark.asyncio
async def test_add_shorturls_raises_already_owned(normal_user: User):
    shorturls = await normal_user.get_shorturls()
    shorturls[0]._owner_pk = PrimaryKey.create_pk_id(1)
    with pytest.raises(exceptions.ShortURLAlreadyOwnedError) as error:
        await normal_user.add_shorturl(shorturls[0])
    assert error.value.owner_pk.get_id() == shorturls[0].owner_pk.get_id()


@pytest.mark.asyncio
async def test_add_shorturls_raises_limit_reached(poor_user: User, normal_shorturl, other_shorturl):
    poor_user.plan._max_shorturls = 1
    await poor_user.add_shorturl(normal_shorturl)
    with pytest.raises(exceptions.ShortURLLimitReachedError) as error:
        await poor_user.add_shorturl(other_shorturl)
    assert error.value.max_shorturls == 1
