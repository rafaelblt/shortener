import pytest

from unittest.mock import NonCallableMagicMock

from shortener.domain import ShortURL, UserID
from shortener.shared.result import Err, Ok
from shortener.shared.validation import IssueCode
from shortener.use_cases.errors import (
    FieldError,
    InvalidInputError,
    NotAuthenticatedError,
)
from shortener.use_cases.list_shorturls import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ListShortURLs,
)
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_page import ShortURLPage
from tests.fixtures.shared.validation import invalid


@pytest.fixture
def list_shorturls(
    shorturl_reader: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> ListShortURLs:
    return ListShortURLs(shorturls=shorturl_reader, current_user=current_user)


@pytest.fixture
def shorturls(
    normal_shorturl: ShortURL, other_shorturl: ShortURL, old_shorturl: ShortURL
) -> list[ShortURL]:
    return [other_shorturl, normal_shorturl, old_shorturl]


@pytest.fixture
def cursor(old_shorturl: ShortURL) -> ShortURLCursor:
    return ShortURLCursor.from_entity(old_shorturl)


def details(*shorturls: ShortURL) -> tuple[ShortURLDetails, ...]:
    return tuple(ShortURLDetails.from_entity(shorturl) for shorturl in shorturls)


async def test_returns_not_authenticated_before_checking_the_input(
    list_shorturls: ListShortURLs,
    current_user: NonCallableMagicMock,
    shorturl_reader: NonCallableMagicMock,
):
    current_user.get_id.return_value = None

    result = await list_shorturls.execute(limit=0)

    assert result == Err(NotAuthenticatedError())
    shorturl_reader.list_by_owner.assert_not_awaited()


@pytest.mark.parametrize(
    "limit, code",
    [
        pytest.param(0, IssueCode.TOO_SMALL, id="zero"),
        pytest.param(-1, IssueCode.TOO_SMALL, id="negative"),
        pytest.param(MAX_PAGE_SIZE + 1, IssueCode.TOO_LARGE, id="above maximum"),
        pytest.param("20", IssueCode.INVALID_TYPE, id="str"),
        pytest.param(True, IssueCode.INVALID_TYPE, id="bool"),
    ],
)
async def test_returns_invalid_input_for_an_invalid_limit_without_reading(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    limit: object,
    code: IssueCode,
):
    result = await list_shorturls.execute(limit=limit)  # type: ignore

    field_error = FieldError("limit", invalid(code).error)
    assert result == Err(InvalidInputError((field_error,)))
    shorturl_reader.list_by_owner.assert_not_awaited()


@pytest.mark.parametrize(
    "arguments, expected_read_limit",
    [
        pytest.param({}, DEFAULT_PAGE_SIZE + 1, id="default"),
        pytest.param({"limit": 1}, 2, id="minimum"),
        pytest.param({"limit": MAX_PAGE_SIZE}, MAX_PAGE_SIZE + 1, id="maximum"),
    ],
)
async def test_reads_one_more_shorturl_of_the_user_than_the_limit(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    owner_id: UserID,
    arguments: dict[str, int],
    expected_read_limit: int,
):
    await list_shorturls.execute(**arguments)
    shorturl_reader.list_by_owner.assert_awaited_once_with(
        owner_id, limit=expected_read_limit, after=None
    )


async def test_reads_after_the_cursor(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    owner_id: UserID,
    cursor: ShortURLCursor,
):
    await list_shorturls.execute(limit=5, cursor=cursor)
    shorturl_reader.list_by_owner.assert_awaited_once_with(
        owner_id, limit=6, after=cursor
    )


@pytest.mark.parametrize(
    "limit, read_count",
    [
        pytest.param(3, 0, id="none"),
        pytest.param(3, 2, id="fewer than the limit"),
        pytest.param(3, 3, id="as many as the limit"),
    ],
)
async def test_returns_all_read_in_order_and_no_cursor_when_none_is_left(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    shorturls: list[ShortURL],
    limit: int,
    read_count: int,
):
    shorturl_reader.list_by_owner.return_value = shorturls[:read_count]

    result = await list_shorturls.execute(limit=limit)

    assert result == Ok(
        ShortURLPage(details(*shorturls[:read_count]), next_cursor=None)
    )


async def test_leaves_out_the_extra_shorturl_and_returns_the_cursor_of_the_last_one(
    list_shorturls: ListShortURLs,
    shorturl_reader: NonCallableMagicMock,
    shorturls: list[ShortURL],
):
    first, second, _extra = shorturls
    shorturl_reader.list_by_owner.return_value = shorturls

    result = await list_shorturls.execute(limit=2)

    assert result == Ok(
        ShortURLPage(details(first, second), ShortURLCursor.from_entity(second))
    )
