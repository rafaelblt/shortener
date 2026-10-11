import asyncio
import pytest

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine

from shortener.domain import (
    ShortURL,
    ShortURLID,
    ShortURLStatus,
    Slug,
    TargetURL,
    UserID,
)
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
from shortener.shared.result import Err, Ok
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_repository import ShortURLReader, SlugTakenError
from shortener.use_cases.unavailable_error import UnavailableError
from tests.fixtures.infra.database import store
from tests.utils.shorturl_helpers import fields_of


UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://user:password@127.0.0.1:1/database"
JANUARY_1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
JANUARY_2 = datetime(2026, 1, 2, tzinfo=timezone.utc)


class TransactionReads:
    """Reads through the transactions of the unit of work, one per read."""

    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def get_by_id(self, id: ShortURLID) -> ShortURL | None:
        async with self._uow.begin() as transaction:
            return await transaction.shorturls.get_by_id(id)

    async def get_by_slug(self, slug: Slug) -> ShortURL | None:
        async with self._uow.begin() as transaction:
            return await transaction.shorturls.get_by_slug(slug)

    async def list_by_owner(
        self, owner_id: UserID, limit: int, after: ShortURLCursor | None
    ) -> list[ShortURL]:
        async with self._uow.begin() as transaction:
            return await transaction.shorturls.list_by_owner(owner_id, limit, after)


@pytest.fixture(params=["reader", "transaction"])
def reads(
    request: pytest.FixtureRequest,
    reader: SQLAlchemyShortURLReader,
    uow: SQLAlchemyUnitOfWork,
) -> ShortURLReader:
    """The reads of both the reader and the repository of a transaction."""
    return reader if request.param == "reader" else TransactionReads(uow)


@pytest.fixture
def changed_shorturl(owner_id: UserID) -> ShortURL:
    """A short URL whose fields all differ from the ones of create()."""
    return ShortURL.restore(
        id=ShortURLID(UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20")),
        slug=Slug("changed"),
        target_url=TargetURL("https://example.com/path?query=1"),
        owner_id=owner_id,
        status=ShortURLStatus.DEACTIVATED,
        resolution_count=3,
        created_at=datetime(
            2026, 1, 1, 12, 30, 15, 123456, tzinfo=timezone(timedelta(hours=-3))
        ),
        last_resolved_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )


def shorturl_of(owner_id: UserID, created_at: datetime, id: int) -> ShortURL:
    return ShortURL.restore(
        id=ShortURLID(UUID(int=id)),
        slug=Slug(f"slug-{id}"),
        target_url=TargetURL("https://example.com"),
        owner_id=owner_id,
        status=ShortURLStatus.ACTIVE,
        resolution_count=0,
        created_at=created_at,
        last_resolved_at=None,
    )


async def test_get_by_id_returns_the_stored_shorturl_with_every_field(
    uow: SQLAlchemyUnitOfWork,
    reads: ShortURLReader,
    changed_shorturl: ShortURL,
):
    await store(uow, changed_shorturl)

    shorturl = await reads.get_by_id(changed_shorturl.id)

    assert shorturl is not None
    assert fields_of(shorturl) == fields_of(changed_shorturl)


async def test_get_by_slug_returns_the_stored_shorturl_with_every_field(
    uow: SQLAlchemyUnitOfWork,
    reads: ShortURLReader,
    changed_shorturl: ShortURL,
):
    await store(uow, changed_shorturl)

    shorturl = await reads.get_by_slug(changed_shorturl.slug)

    assert shorturl is not None
    assert fields_of(shorturl) == fields_of(changed_shorturl)


@pytest.mark.parametrize(
    "read",
    [
        pytest.param(
            lambda reads: reads.get_by_id(ShortURLID(UUID(int=1))), id="other id"
        ),
        pytest.param(
            lambda reads: reads.get_by_slug(Slug("other-slug")), id="other slug"
        ),
        pytest.param(
            lambda reads: reads.get_by_slug(Slug("LOREM-IPSUM-WEBSITE")),
            id="slug in another case",
        ),
    ],
)
async def test_reads_return_none_when_no_shorturl_matches(
    reads: ShortURLReader, stored_shorturl: ShortURL, read
):
    assert await read(reads) is None


async def test_reads_a_shorturl_whose_values_break_the_current_rules_of_create(
    uow: SQLAlchemyUnitOfWork,
    reads: ShortURLReader,
    owner_id: UserID,
    now: datetime,
):
    shorturl = ShortURL.create(
        slug=Slug.parse("a.b"),
        target_url=TargetURL.parse("http://insecure.com"),
        owner_id=owner_id,
        now=now,
    )
    await store(uow, shorturl)

    read = await reads.get_by_slug(Slug.parse("a.b"))

    assert read is not None
    assert fields_of(read) == fields_of(shorturl)


async def test_list_by_owner_returns_the_shorturls_of_the_owner_newest_first(
    uow: SQLAlchemyUnitOfWork,
    reads: ShortURLReader,
    owner_id: UserID,
    other_user_id: UserID,
):
    older = shorturl_of(owner_id, JANUARY_1, id=3)
    newer_with_smaller_id = shorturl_of(owner_id, JANUARY_2, id=1)
    newer_with_larger_id = shorturl_of(owner_id, JANUARY_2, id=2)
    of_another_user = shorturl_of(other_user_id, JANUARY_2, id=4)
    await store(
        uow, older, of_another_user, newer_with_smaller_id, newer_with_larger_id
    )

    listed = await reads.list_by_owner(owner_id, limit=10, after=None)

    assert [shorturl.id for shorturl in listed] == [
        newer_with_larger_id.id,
        newer_with_smaller_id.id,
        older.id,
    ]


async def test_list_by_owner_returns_at_most_limit_shorturls(
    uow: SQLAlchemyUnitOfWork, reads: ShortURLReader, owner_id: UserID
):
    await store(uow, *(shorturl_of(owner_id, JANUARY_1, id=id) for id in (1, 2, 3)))

    listed = await reads.list_by_owner(owner_id, limit=2, after=None)

    assert [shorturl.id.value for shorturl in listed] == [UUID(int=3), UUID(int=2)]


@pytest.mark.parametrize(
    "after_id, expected_ids",
    [
        pytest.param(3, [2, 1], id="the newest, with the same created_at as the next"),
        pytest.param(2, [1], id="one with an earlier created_at after it"),
        pytest.param(1, [], id="the oldest"),
    ],
)
async def test_list_by_owner_returns_only_the_shorturls_after_the_cursor(
    uow: SQLAlchemyUnitOfWork,
    reads: ShortURLReader,
    owner_id: UserID,
    after_id: int,
    expected_ids: list[int],
):
    shorturls = {
        1: shorturl_of(owner_id, JANUARY_1, id=1),
        2: shorturl_of(owner_id, JANUARY_2, id=2),
        3: shorturl_of(owner_id, JANUARY_2, id=3),
    }
    await store(uow, *shorturls.values())

    listed = await reads.list_by_owner(
        owner_id, limit=10, after=ShortURLCursor.from_entity(shorturls[after_id])
    )

    assert [shorturl.id.value for shorturl in listed] == [
        UUID(int=id) for id in expected_ids
    ]


async def test_list_by_owner_returns_an_empty_list_for_an_owner_without_shorturls(
    reads: ShortURLReader,
    stored_shorturl: ShortURL,
    other_user_id: UserID,
):
    assert await reads.list_by_owner(other_user_id, limit=10, after=None) == []


async def test_add_returns_ok(uow: SQLAlchemyUnitOfWork, normal_shorturl: ShortURL):
    async with uow.begin() as transaction:
        assert await transaction.shorturls.add(normal_shorturl) == Ok(None)


async def test_add_returns_slug_taken_when_another_shorturl_has_the_slug(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    stored_shorturl: ShortURL,
    other_user_id: UserID,
    now: datetime,
):
    same_slug = ShortURL.create(
        slug=stored_shorturl.slug,
        target_url=TargetURL("https://other.com"),
        owner_id=other_user_id,
        now=now,
    )

    async with uow.begin() as transaction:
        result = await transaction.shorturls.add(same_slug)
        await transaction.commit()

    assert result == Err(SlugTakenError(stored_shorturl.slug))
    assert await reader.get_by_id(same_slug.id) is None


async def test_add_raises_when_another_shorturl_has_the_id(
    uow: SQLAlchemyUnitOfWork, stored_shorturl: ShortURL
):
    same_id = ShortURL.restore(
        id=stored_shorturl.id,
        slug=Slug("other-slug"),
        target_url=stored_shorturl.target_url,
        owner_id=stored_shorturl.owner_id,
        status=stored_shorturl.status,
        resolution_count=stored_shorturl.resolution_count,
        created_at=stored_shorturl.created_at,
        last_resolved_at=stored_shorturl.last_resolved_at,
    )

    async with uow.begin() as transaction:
        with pytest.raises(IntegrityError):
            await transaction.shorturls.add(same_id)


async def test_slugs_that_differ_only_in_case_are_different_slugs(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    owner_id: UserID,
    now: datetime,
):
    upper = ShortURL.create(
        slug=Slug("ABC"),
        target_url=TargetURL("https://upper.com"),
        owner_id=owner_id,
        now=now,
    )
    lower = ShortURL.create(
        slug=Slug("abc"),
        target_url=TargetURL("https://lower.com"),
        owner_id=owner_id,
        now=now,
    )

    await store(uow, upper, lower)

    read = await reader.get_by_slug(Slug("ABC"))
    assert read is not None
    assert read.id == upper.id


async def test_save_stores_every_field(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    stored_shorturl: ShortURL,
    now: datetime,
):
    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(stored_shorturl.id)
        assert shorturl is not None
        shorturl.change_slug(Slug("new-slug"))
        shorturl.change_target_url(TargetURL("https://new.com"))
        shorturl.resolve(now + timedelta(days=1))
        shorturl.disable()
        result = await transaction.shorturls.save(shorturl)
        await transaction.commit()

    assert result == Ok(None)
    saved = await reader.get_by_id(stored_shorturl.id)
    assert saved is not None
    assert fields_of(saved) == fields_of(shorturl)


async def test_save_returns_ok_when_the_shorturl_keeps_its_slug(
    uow: SQLAlchemyUnitOfWork, stored_shorturl: ShortURL
):
    async with uow.begin() as transaction:
        assert await transaction.shorturls.save(stored_shorturl) == Ok(None)


async def test_save_returns_slug_taken_when_another_shorturl_has_the_slug(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await store(uow, normal_shorturl, other_shorturl)

    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(other_shorturl.id)
        assert shorturl is not None
        shorturl.change_slug(normal_shorturl.slug)
        result = await transaction.shorturls.save(shorturl)
        await transaction.commit()

    assert result == Err(SlugTakenError(normal_shorturl.slug))
    stored = await reader.get_by_id(other_shorturl.id)
    assert stored is not None
    assert stored.slug == other_shorturl.slug


async def test_the_transaction_goes_on_after_add_returns_slug_taken(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    stored_shorturl: ShortURL,
    other_shorturl: ShortURL,
    old_shorturl: ShortURL,
):
    async with uow.begin() as transaction:
        (await transaction.shorturls.add(other_shorturl)).unwrap()
        old_shorturl.change_slug(stored_shorturl.slug)
        await transaction.shorturls.add(old_shorturl)
        old_shorturl.change_slug(Slug("free-slug"))
        retried = await transaction.shorturls.add(old_shorturl)
        await transaction.commit()

    assert retried == Ok(None)
    assert await reader.get_by_id(other_shorturl.id) is not None
    assert await reader.get_by_id(old_shorturl.id) is not None


async def test_the_transaction_goes_on_after_save_returns_slug_taken(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await store(uow, normal_shorturl, other_shorturl)

    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(other_shorturl.id)
        assert shorturl is not None
        shorturl.change_slug(normal_shorturl.slug)
        await transaction.shorturls.save(shorturl)
        shorturl.change_slug(Slug("free-slug"))
        retried = await transaction.shorturls.save(shorturl)
        await transaction.commit()

    assert retried == Ok(None)
    saved = await reader.get_by_id(other_shorturl.id)
    assert saved is not None
    assert saved.slug == Slug("free-slug")


async def test_remove_deletes_only_the_shorturl(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
):
    await store(uow, normal_shorturl, other_shorturl)

    async with uow.begin() as transaction:
        await transaction.shorturls.remove(normal_shorturl)
        await transaction.commit()

    assert await reader.get_by_id(normal_shorturl.id) is None
    assert await reader.get_by_id(other_shorturl.id) is not None


async def test_the_reader_does_not_wait_for_a_shorturl_a_transaction_read(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    stored_shorturl: ShortURL,
):
    async with uow.begin() as transaction:
        await transaction.shorturls.get_by_id(stored_shorturl.id)
        async with asyncio.timeout(5):
            assert await reader.get_by_id(stored_shorturl.id) is not None


async def test_the_reader_does_not_read_what_a_transaction_has_not_committed(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
):
    async with uow.begin() as transaction:
        await transaction.shorturls.add(normal_shorturl)
        assert await reader.get_by_id(normal_shorturl.id) is None


async def test_the_reader_raises_unavailable_when_the_database_is_unreachable():
    engine = create_async_engine(UNREACHABLE_DATABASE_URL)
    try:
        with pytest.raises(UnavailableError) as raised:
            await SQLAlchemyShortURLReader(engine).get_by_id(ShortURLID(UUID(int=1)))
        assert isinstance(raised.value.__cause__, OSError)
    finally:
        await engine.dispose()


async def test_reads_raise_the_error_of_the_database_when_trying_again_would_not_fix_it(
    database_url: str,
):
    # Without the table in the search path, the database answers that it
    # doesn't exist.
    engine = create_async_engine(
        database_url, connect_args={"server_settings": {"search_path": "missing"}}
    )
    try:
        with pytest.raises(ProgrammingError):
            await SQLAlchemyShortURLReader(engine).get_by_id(ShortURLID(UUID(int=1)))
    finally:
        await engine.dispose()
