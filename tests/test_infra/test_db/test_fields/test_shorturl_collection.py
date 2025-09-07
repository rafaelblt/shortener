import pytest

from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.user.user import User


@pytest.mark.asyncio
async def test_get_all_without_shorturls(persistent_poor_user: User):
    retrieved = await persistent_poor_user.get_shorturls()
    assert retrieved == []


@pytest.mark.asyncio
async def test_add(persistent_poor_user: User, persistent_normal_shorturl: ShortURL):
    await persistent_poor_user.add_shorturl(persistent_normal_shorturl)
    retrieved = await persistent_poor_user.get_shorturls()
    assert retrieved[0].slug == persistent_normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_all_with_shorturls(persistent_normal_user: User, normal_user: User):
    retrieved = await persistent_normal_user.get_shorturls()
    expected = await normal_user.get_shorturls()
    assert [s.slug for s in retrieved] == [s.slug for s in expected]


@pytest.mark.asyncio
async def test_get_by_pk(persistent_normal_user: User, persistent_normal_shorturl: ShortURL):
    retrieved = await persistent_normal_user.shorturls.get_by_pk(
        persistent_normal_shorturl.pk
    )
    assert retrieved is not None
    assert retrieved.slug == persistent_normal_shorturl.slug


@pytest.mark.asyncio
async def test_get_by_slug(persistent_normal_user: User, persistent_normal_shorturl: ShortURL):
    retrieved = await persistent_normal_user.shorturls.get_by_slug(
        persistent_normal_shorturl.slug
    )
    assert retrieved is not None
    assert retrieved.pk == persistent_normal_shorturl.pk


@pytest.mark.asyncio
async def test_remove_by_pk(persistent_normal_user: User, persistent_normal_shorturl: ShortURL):
    retrieved = await persistent_normal_user.shorturls.remove_by_pk(
        persistent_normal_shorturl.pk
    )
    assert retrieved is not None
    assert retrieved.slug == persistent_normal_shorturl.slug
    assert await persistent_normal_user.get_shorturls() == []


@pytest.mark.asyncio
async def test_count(persistent_normal_user: User):
    retrieved = await persistent_normal_user.shorturls.count()
    assert retrieved == 1
