from unittest.mock import NonCallableMagicMock

import pytest

from shortener.domain import ShortURL, ShortURLID, UserID
from shortener.shared.result import Err, Ok
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from tests.fixtures.use_cases.doubles import call_names


@pytest.fixture
def delete_shorturl(
    uow: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> DeleteShortURL:
    return DeleteShortURL(uow=uow, current_user=current_user)


@pytest.fixture
def shorturl(transaction: NonCallableMagicMock, normal_shorturl: ShortURL) -> ShortURL:
    transaction.shorturls.get_by_id.return_value = normal_shorturl
    return normal_shorturl


async def test_returns_not_authenticated_without_beginning_a_transaction(
    delete_shorturl: DeleteShortURL,
    current_user: NonCallableMagicMock,
    uow: NonCallableMagicMock,
    shorturl: ShortURL,
):
    current_user.get_id.return_value = None

    result = await delete_shorturl.execute(shorturl.id.value)

    assert result == Err(NotAuthenticatedError())
    uow.begin.assert_not_called()


async def test_reads_the_shorturl_by_id_through_the_transaction(
    delete_shorturl: DeleteShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    await delete_shorturl.execute(shorturl.id.value)
    transaction.shorturls.get_by_id.assert_awaited_once_with(
        ShortURLID(shorturl.id.value)
    )


async def test_raises_for_an_id_that_is_not_a_uuid_before_beginning_a_transaction(
    delete_shorturl: DeleteShortURL, uow: NonCallableMagicMock, shorturl: ShortURL
):
    with pytest.raises(TypeError):
        await delete_shorturl.execute(str(shorturl.id.value))  # type: ignore
    uow.begin.assert_not_called()


async def test_returns_not_found_without_removing_when_no_shorturl_has_the_id(
    delete_shorturl: DeleteShortURL,
    transaction: NonCallableMagicMock,
    normal_shorturl: ShortURL,
):
    result = await delete_shorturl.execute(normal_shorturl.id.value)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.remove.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_returns_not_found_without_removing_a_shorturl_of_another_user(
    delete_shorturl: DeleteShortURL,
    current_user: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
    other_user_id: UserID,
):
    current_user.get_id.return_value = other_user_id

    result = await delete_shorturl.execute(shorturl.id.value)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.remove.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_removes_the_shorturl_and_then_commits(
    delete_shorturl: DeleteShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    await delete_shorturl.execute(shorturl.id.value)

    transaction.shorturls.remove.assert_awaited_once_with(shorturl)
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == [
        "shorturls.get_by_id",
        "shorturls.remove",
        "commit",
    ]


async def test_returns_ok_with_none_after_removing(
    delete_shorturl: DeleteShortURL, shorturl: ShortURL
):
    assert await delete_shorturl.execute(shorturl.id.value) == Ok(None)
