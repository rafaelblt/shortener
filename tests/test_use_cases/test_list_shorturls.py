import pytest

from unittest.mock import NonCallableMagicMock

from shortener.domain import ShortURL, UserID
from shortener.shared.result import Err, Ok
from shortener.use_cases.errors import NotAuthenticatedError
from shortener.use_cases.list_shorturls import ListShortURLs
from shortener.use_cases.shorturl_details import ShortURLDetails


@pytest.fixture
def list_shorturls(
    shorturl_reader: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> ListShortURLs:
    return ListShortURLs(shorturls=shorturl_reader, current_user=current_user)


async def test_returns_not_authenticated_without_reading(
    list_shorturls: ListShortURLs,
    current_user: NonCallableMagicMock,
    shorturl_reader: NonCallableMagicMock,
):
    current_user.get_id.return_value = None

    result = await list_shorturls.execute()

    assert result == Err(NotAuthenticatedError())
    shorturl_reader.list_by_owner.assert_not_awaited()


async def test_lists_the_shorturls_owned_by_the_user(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    owner_id: UserID,
):
    await list_shorturls.execute()
    shorturl_reader.list_by_owner.assert_awaited_once_with(owner_id)


async def test_returns_the_details_of_each_shorturl_in_the_order_read(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
    old_shorturl: ShortURL,
):
    shorturls = [other_shorturl, old_shorturl, normal_shorturl]
    shorturl_reader.list_by_owner.return_value = shorturls

    result = await list_shorturls.execute()

    assert result == Ok(tuple(ShortURLDetails.from_entity(each) for each in shorturls))


async def test_returns_an_empty_tuple_when_the_user_has_no_shorturls(
    list_shorturls: ListShortURLs,
):
    assert await list_shorturls.execute() == Ok(())
