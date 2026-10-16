from datetime import datetime
from unittest.mock import NonCallableMagicMock

import pytest

from shortener.domain import ShortURL, Slug
from shortener.domain.errors import ShortURLDeactivatedError
from shortener.shared.result import Err, Ok
from shortener.use_cases.errors import ShortURLNotFoundError
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.resolved_slug import ResolvedSlug
from shortener.use_cases.shorturl_repository import SlugTakenError
from tests.fixtures.use_cases.doubles import call_names, record_copies


@pytest.fixture
def resolve_slug(uow: NonCallableMagicMock, clock: NonCallableMagicMock) -> ResolveSlug:
    return ResolveSlug(uow=uow, clock=clock)


@pytest.fixture
def shorturl(transaction: NonCallableMagicMock, normal_shorturl: ShortURL) -> ShortURL:
    transaction.shorturls.get_by_slug.return_value = normal_shorturl
    return normal_shorturl


@pytest.mark.parametrize(
    "slug",
    [
        pytest.param("my-slug", id="valid"),
        pytest.param("ab", id="too short"),
        pytest.param("dot.slug", id="invalid format"),
    ],
)
async def test_reads_the_shorturl_of_any_non_empty_slug_through_the_transaction(
    resolve_slug: ResolveSlug, transaction: NonCallableMagicMock, slug: str
):
    await resolve_slug.execute(slug)
    transaction.shorturls.get_by_slug.assert_awaited_once_with(Slug.parse(slug))


@pytest.mark.parametrize(
    "slug, error",
    [
        pytest.param("", ValueError, id="empty"),
        pytest.param(None, TypeError, id="None"),
    ],
)
async def test_raises_for_a_slug_that_parse_rejects_before_beginning_a_transaction(
    resolve_slug: ResolveSlug,
    uow: NonCallableMagicMock,
    slug: object,
    error: type[Exception],
):
    with pytest.raises(error):
        await resolve_slug.execute(slug)  # type: ignore[arg-type]
    uow.begin.assert_not_called()


async def test_returns_not_found_when_no_shorturl_has_the_slug(
    resolve_slug: ResolveSlug, transaction: NonCallableMagicMock
):
    result = await resolve_slug.execute("my-slug")

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_returns_the_target_url_of_an_active_shorturl(
    resolve_slug: ResolveSlug, shorturl: ShortURL
):
    result = await resolve_slug.execute(shorturl.slug)
    assert result == Ok(ResolvedSlug(target_url=shorturl.target_url))


async def test_saves_the_shorturl_with_the_resolution_counted_and_then_commits(
    resolve_slug: ResolveSlug,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
    now: datetime,
):
    saved = record_copies(transaction.shorturls.save)

    await resolve_slug.execute(shorturl.slug)

    transaction.shorturls.save.assert_awaited_once_with(shorturl)
    assert saved[0].resolution_count == 1
    assert saved[0].last_resolved_at == now
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == [
        "shorturls.get_by_slug",
        "shorturls.save",
        "commit",
    ]


async def test_returns_the_error_of_a_deactivated_shorturl_without_saving(
    resolve_slug: ResolveSlug, transaction: NonCallableMagicMock, shorturl: ShortURL
):
    shorturl.disable()

    result = await resolve_slug.execute(shorturl.slug)

    assert result == Err(ShortURLDeactivatedError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_raises_without_committing_if_save_returns_slug_taken(
    resolve_slug: ResolveSlug, transaction: NonCallableMagicMock, shorturl: ShortURL
):
    transaction.shorturls.save.return_value = Err(SlugTakenError(shorturl.slug))

    with pytest.raises(ValueError):
        await resolve_slug.execute(shorturl.slug)
    transaction.commit.assert_not_awaited()
