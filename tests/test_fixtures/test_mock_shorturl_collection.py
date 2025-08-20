import pytest

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl.shorturl import ShortURL
from tests.fixtures import MockShortURLCollection


@pytest.fixture
def collection(mock_shorturl_collection):
    return mock_shorturl_collection


def test_add(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    assert collection._items == [normal_shorturl, old_shorturl, other_shorturl]


def test_get_all(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.get_all()

    assert retrieved == collection._items


def test_get_by_pk(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.get_by_pk(old_shorturl.pk)

    assert retrieved == old_shorturl


def test_get_by_pk_non_existent(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.get_by_pk(PrimaryKey.create_pk_id(4))

    assert retrieved is None


def test_get_by_slug(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.get_by_slug(old_shorturl.slug)

    assert retrieved == old_shorturl


def test_get_by_slug_non_existent(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    collection.add(normal_shorturl)
    collection.add(old_shorturl)

    retrieved = collection.get_by_slug(other_shorturl.slug)

    assert retrieved is None


def test_remove_by_pk(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.remove_by_pk(old_shorturl.pk)

    assert retrieved == old_shorturl
    assert old_shorturl not in collection.get_all()


def test_remove_by_pk_non_existent(
    collection: MockShortURLCollection,
    normal_shorturl: ShortURL,
    old_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    normal_shorturl._pk = PrimaryKey.create_pk_id(1)
    old_shorturl._pk = PrimaryKey.create_pk_id(2)
    other_shorturl._pk = PrimaryKey.create_pk_id(3)

    collection.add(normal_shorturl)
    collection.add(old_shorturl)
    collection.add(other_shorturl)

    retrieved = collection.remove_by_pk(PrimaryKey.create_pk_id(4))

    assert retrieved is None
    assert len(collection.get_all()) == 3
