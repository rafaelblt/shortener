from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import NotAuthenticatedError
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import ShortURLReader


type ListShortURLsError = NotAuthenticatedError


class ListShortURLs:

    def __init__(self, shorturls: ShortURLReader, current_user: CurrentUser):
        self._shorturls = shorturls
        self._current_user = current_user

    async def execute(self) -> Result[tuple[ShortURLDetails, ...], ListShortURLsError]:
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())
        shorturls = await self._shorturls.list_by_owner(user_id)
        return Ok(
            tuple(ShortURLDetails.from_entity(shorturl) for shorturl in shorturls)
        )
