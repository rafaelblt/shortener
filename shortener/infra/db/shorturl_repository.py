from sqlalchemy import (
    Insert,
    Row,
    Select,
    Update,
    delete,
    insert,
    select,
    tuple_,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from shortener.domain import (
    ShortURL,
    ShortURLID,
    ShortURLStatus,
    Slug,
    TargetURL,
    UserID,
)
from shortener.infra.db.tables import SLUG_UNIQUE_CONSTRAINT, shorturls
from shortener.infra.db.transient_errors import unavailable_when_transient
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_repository import SlugTakenError


class SQLAlchemyShortURLRepository:
    """
    The shorturls of a transaction. What it reads stays locked until the
    transaction ends. See docs/use_cases.md#concurrency
    """

    def __init__(self, connection: AsyncConnection):
        self._connection = connection

    async def get_by_id(self, id: ShortURLID) -> ShortURL | None:
        return _first(await self._read(_select_by_id(id)))

    async def get_by_slug(self, slug: Slug) -> ShortURL | None:
        return _first(await self._read(_select_by_slug(slug)))

    async def list_by_owner(
        self, owner_id: UserID, limit: int, after: ShortURLCursor | None
    ) -> list[ShortURL]:
        return await self._read(_select_by_owner(owner_id, limit, after))

    async def add(self, shorturl: ShortURL) -> Result[None, SlugTakenError]:
        return await self._write(
            insert(shorturls).values(id=shorturl.id.value, **_columns(shorturl)),
            shorturl.slug,
        )

    async def save(self, shorturl: ShortURL) -> Result[None, SlugTakenError]:
        return await self._write(
            update(shorturls)
            .where(shorturls.c.id == shorturl.id.value)
            .values(**_columns(shorturl)),
            shorturl.slug,
        )

    async def remove(self, shorturl: ShortURL) -> None:
        with unavailable_when_transient():
            await self._connection.execute(
                delete(shorturls).where(shorturls.c.id == shorturl.id.value)
            )

    async def _read(self, statement: Select) -> list[ShortURL]:
        with unavailable_when_transient():
            result = await self._connection.execute(statement.with_for_update())
            rows = result.all()
        return [_to_shorturl(row) for row in rows]

    async def _write(
        self, statement: Insert | Update, slug: Slug
    ) -> Result[None, SlugTakenError]:
        # In a savepoint, a taken slug rolls back only this write, and the
        # transaction goes on. See docs/use_cases.md#reading-and-writing
        try:
            with unavailable_when_transient():
                async with self._connection.begin_nested():
                    await self._connection.execute(statement)
        except IntegrityError as error:
            if not _is_slug_taken(error):
                raise
            return Err(SlugTakenError(slug))
        return Ok(None)


class SQLAlchemyShortURLReader:
    """Reads outside of any transaction, without locking."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def get_by_id(self, id: ShortURLID) -> ShortURL | None:
        return _first(await self._read(_select_by_id(id)))

    async def get_by_slug(self, slug: Slug) -> ShortURL | None:
        return _first(await self._read(_select_by_slug(slug)))

    async def list_by_owner(
        self, owner_id: UserID, limit: int, after: ShortURLCursor | None
    ) -> list[ShortURL]:
        return await self._read(_select_by_owner(owner_id, limit, after))

    async def _read(self, statement: Select) -> list[ShortURL]:
        with unavailable_when_transient():
            async with self._engine.connect() as connection:
                rows = (await connection.execute(statement)).all()
        return [_to_shorturl(row) for row in rows]


def _select_by_id(id: ShortURLID) -> Select:
    return select(shorturls).where(shorturls.c.id == id.value)


def _select_by_slug(slug: Slug) -> Select:
    return select(shorturls).where(shorturls.c.slug == str(slug))


def _select_by_owner(
    owner_id: UserID, limit: int, after: ShortURLCursor | None
) -> Select:
    statement = (
        select(shorturls)
        .where(shorturls.c.owner_id == owner_id.value)
        .order_by(shorturls.c.created_at.desc(), shorturls.c.id.desc())
        .limit(limit)
    )
    if after is None:
        return statement
    return statement.where(
        tuple_(shorturls.c.created_at, shorturls.c.id)
        < tuple_(after.created_at, after.id)
    )


def _first(shorturls: list[ShortURL]) -> ShortURL | None:
    return shorturls[0] if shorturls else None


def _columns(shorturl: ShortURL) -> dict[str, object]:
    return {
        "slug": str(shorturl.slug),
        "target_url": str(shorturl.target_url),
        "owner_id": shorturl.owner_id.value,
        "status": shorturl.status.value,
        "resolution_count": shorturl.resolution_count,
        "created_at": shorturl.created_at,
        "last_resolved_at": shorturl.last_resolved_at,
    }


def _to_shorturl(row: Row) -> ShortURL:
    # parse(), and not create(), since a stored value may have been created
    # under older rules. See docs/domain.md#value-objects
    return ShortURL.restore(
        id=ShortURLID(row.id),
        slug=Slug.parse(row.slug),
        target_url=TargetURL.parse(row.target_url),
        owner_id=UserID(row.owner_id),
        status=ShortURLStatus(row.status),
        resolution_count=row.resolution_count,
        created_at=row.created_at,
        last_resolved_at=row.last_resolved_at,
    )


def _is_slug_taken(error: IntegrityError) -> bool:
    # The dialect of SQLAlchemy raises its error from the one of asyncpg, and
    # only the one of asyncpg names the constraint.
    return (
        getattr(error.orig.__cause__, "constraint_name", None)
        == SLUG_UNIQUE_CONSTRAINT
    )
