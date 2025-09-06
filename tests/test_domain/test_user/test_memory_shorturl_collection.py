import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.user.fields import InMemoryShortURLCollection


@pytest.fixture
def collection():
    return InMemoryShortURLCollection()


@pytest.mark.asyncio
async def test_add(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    assert collection._shorturls == [normal_shorturl, old_shorturl, other_shorturl]


@pytest.mark.asyncio
async def test_get_all(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.get_all()

    assert retrieved == collection._shorturls


@pytest.mark.asyncio
async def test_get_by_pk(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.get_by_pk(old_shorturl.pk)

    assert retrieved == old_shorturl


@pytest.mark.asyncio
async def test_get_by_pk_non_existent(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.get_by_pk(PrimaryKey.create_pk_id(4))

    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_slug(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.get_by_slug(old_shorturl.slug)

    assert retrieved == old_shorturl


@pytest.mark.asyncio
async def test_get_by_slug_non_existent(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)

    retrieved = await collection.get_by_slug(other_shorturl.slug)

    assert retrieved is None


@pytest.mark.asyncio
async def test_remove_by_pk(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.remove_by_pk(old_shorturl.pk)

    assert retrieved == old_shorturl
    assert old_shorturl not in await collection.get_all()


@pytest.mark.asyncio
async def test_remove_by_pk_first_position(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.remove_by_pk(normal_shorturl.pk)

    assert retrieved == normal_shorturl
    assert normal_shorturl not in await collection.get_all()


@pytest.mark.asyncio
async def test_remove_by_pk_non_existent(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.remove_by_pk(PrimaryKey.create_pk_id(4))

    assert retrieved is None
    assert len(await collection.get_all()) == 3


@pytest.mark.asyncio
async def test_remove_by_pk_undefined(collection: InMemoryShortURLCollection):
    with pytest.raises(ValueError, match="The provided PK is undefined."):
        await collection.remove_by_pk(PrimaryKey.create_pk_undefined())


@pytest.mark.asyncio
async def test_count(
    collection: InMemoryShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    await collection.add(normal_shorturl)
    await collection.add(old_shorturl)
    await collection.add(other_shorturl)

    retrieved = await collection.count()

    assert retrieved == 3
