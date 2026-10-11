from typing import Final

from shortener.shared.result import Err, Ok, Result
from shortener.shared.validation import IntegerValidation
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import (
    InvalidInputError,
    NotAuthenticatedError,
    collect_field_errors,
)
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_page import ShortURLPage
from shortener.use_cases.shorturl_repository import ShortURLReader


DEFAULT_PAGE_SIZE: Final = 20
MAX_PAGE_SIZE: Final = 100

type ListShortURLsError = NotAuthenticatedError | InvalidInputError


class ListShortURLs:

    def __init__(self, shorturls: ShortURLReader, current_user: CurrentUser):
        self._shorturls = shorturls
        self._current_user = current_user

    async def execute(
        self, limit: int = DEFAULT_PAGE_SIZE, cursor: ShortURLCursor | None = None
    ) -> Result[ShortURLPage, ListShortURLsError]:
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())

        limit_result = (
            IntegerValidation(limit).min_value(1).max_value(MAX_PAGE_SIZE).result()
        )
        if field_errors := collect_field_errors(limit=limit_result):
            return Err(InvalidInputError(field_errors))

        # One more than the page holds, to know whether there is a next page.
        shorturls = await self._shorturls.list_by_owner(
            user_id, limit=limit + 1, after=cursor
        )
        page = shorturls[:limit]
        next_cursor = (
            ShortURLCursor.from_entity(page[-1]) if len(shorturls) > limit else None
        )
        return Ok(
            ShortURLPage(
                items=tuple(ShortURLDetails.from_entity(each) for each in page),
                next_cursor=next_cursor,
            )
        )
