from unittest.mock import NonCallableMagicMock

import pytest

from shortener.domain import ShortURL, ShortURLID, UserID
from shortener.shared.result import Err, Ok
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.shorturl_details import ShortURLDetails


@pytest.fixture
def get_shorturl(
    shorturl_reader: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> GetShortURL:
    return GetShortURL(shorturls=shorturl_reader, current_user=current_user)


@pytest.fixture
def shorturl(
    shorturl_reader: NonCallableMagicMock, normal_shorturl: ShortURL
) -> ShortURL:
    shorturl_reader.get_by_id.return_value = normal_shorturl
    return normal_shorturl


async def test_returns_not_authenticated_without_reading(
    get_shorturl: GetShortURL,
    current_user: NonCallableMagicMock,
    shorturl_reader: NonCallableMagicMock,
    shorturl: ShortURL,
):
    current_user.get_id.return_value = None

    result = await get_shorturl.execute(shorturl.id.value)

    assert result == Err(NotAuthenticatedError())
    shorturl_reader.get_by_id.assert_not_awaited()


async def test_reads_the_shorturl_by_id(
    get_shorturl: GetShortURL,
    shorturl_reader: NonCallableMagicMock,
    shorturl: ShortURL,
):
    await get_shorturl.execute(shorturl.id.value)
    shorturl_reader.get_by_id.assert_awaited_once_with(ShortURLID(shorturl.id.value))


async def test_raises_for_an_id_that_is_not_a_uuid(
    get_shorturl: GetShortURL, shorturl: ShortURL
):
    with pytest.raises(TypeError):
        await get_shorturl.execute(str(shorturl.id.value))  # type: ignore[arg-type]


async def test_returns_not_found_when_no_shorturl_has_the_id(
    get_shorturl: GetShortURL, normal_shorturl: ShortURL
):
    result = await get_shorturl.execute(normal_shorturl.id.value)
    assert result == Err(ShortURLNotFoundError())


async def test_returns_not_found_for_a_shorturl_of_another_user(
    get_shorturl: GetShortURL,
    current_user: NonCallableMagicMock,
    shorturl: ShortURL,
    other_user_id: UserID,
):
    current_user.get_id.return_value = other_user_id

    result = await get_shorturl.execute(shorturl.id.value)

    assert result == Err(ShortURLNotFoundError())


async def test_returns_the_details_of_a_shorturl_of_the_user(
    get_shorturl: GetShortURL, shorturl: ShortURL
):
    result = await get_shorturl.execute(shorturl.id.value)
    assert result == Ok(ShortURLDetails.from_entity(shorturl))
