import pytest

from unittest.mock import NonCallableMagicMock

from shortener.domain import ShortURL, ShortURLID, ShortURLStatus, UserID
from shortener.shared.result import Err, Ok
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import SlugTakenError
from tests.fixtures.use_cases.doubles import call_names, record_copies


@pytest.fixture
def enable_shorturl(
    uow: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> EnableShortURL:
    return EnableShortURL(uow=uow, current_user=current_user)


@pytest.fixture
def shorturl(transaction: NonCallableMagicMock, normal_shorturl: ShortURL) -> ShortURL:
    normal_shorturl.disable()
    transaction.shorturls.get_by_id.return_value = normal_shorturl
    return normal_shorturl


async def test_returns_not_authenticated_without_beginning_a_transaction(
    enable_shorturl: EnableShortURL,
    current_user: NonCallableMagicMock,
    uow: NonCallableMagicMock,
    shorturl: ShortURL,
):
    current_user.get_id.return_value = None

    result = await enable_shorturl.execute(shorturl.id.value)

    assert result == Err(NotAuthenticatedError())
    uow.begin.assert_not_called()


async def test_reads_the_shorturl_by_id_through_the_transaction(
    enable_shorturl: EnableShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    await enable_shorturl.execute(shorturl.id.value)
    transaction.shorturls.get_by_id.assert_awaited_once_with(
        ShortURLID(shorturl.id.value)
    )


async def test_raises_for_an_id_that_is_not_a_uuid_before_beginning_a_transaction(
    enable_shorturl: EnableShortURL, uow: NonCallableMagicMock, shorturl: ShortURL
):
    with pytest.raises(TypeError):
        await enable_shorturl.execute(str(shorturl.id.value))  # type: ignore
    uow.begin.assert_not_called()


async def test_returns_not_found_without_saving_when_no_shorturl_has_the_id(
    enable_shorturl: EnableShortURL,
    transaction: NonCallableMagicMock,
    normal_shorturl: ShortURL,
):
    result = await enable_shorturl.execute(normal_shorturl.id.value)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_returns_not_found_without_saving_for_a_shorturl_of_another_user(
    enable_shorturl: EnableShortURL,
    current_user: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
    other_user_id: UserID,
):
    current_user.get_id.return_value = other_user_id

    result = await enable_shorturl.execute(shorturl.id.value)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_saves_the_shorturl_active_and_then_commits(
    enable_shorturl: EnableShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    saved = record_copies(transaction.shorturls.save)

    await enable_shorturl.execute(shorturl.id.value)

    transaction.shorturls.save.assert_awaited_once_with(shorturl)
    assert saved[0].status == ShortURLStatus.ACTIVE
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == [
        "shorturls.get_by_id",
        "shorturls.save",
        "commit",
    ]


async def test_returns_the_details_of_the_enabled_shorturl(
    enable_shorturl: EnableShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    saved = record_copies(transaction.shorturls.save)

    result = await enable_shorturl.execute(shorturl.id.value)

    assert result == Ok(ShortURLDetails.from_entity(saved[0]))


async def test_raises_without_committing_if_save_returns_slug_taken(
    enable_shorturl: EnableShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    transaction.shorturls.save.return_value = Err(SlugTakenError(shorturl.slug))

    with pytest.raises(ValueError):
        await enable_shorturl.execute(shorturl.id.value)
    transaction.commit.assert_not_awaited()
