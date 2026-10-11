from uuid import UUID

from shortener.domain import ShortURLID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import ShortURLReader


type GetShortURLError = NotAuthenticatedError | ShortURLNotFoundError


class GetShortURL:

    def __init__(self, shorturls: ShortURLReader, current_user: CurrentUser):
        self._shorturls = shorturls
        self._current_user = current_user

    async def execute(self, id: UUID) -> Result[ShortURLDetails, GetShortURLError]:
        """
        Raises:
            TypeError: The id isn't a UUID.
        """
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())
        shorturl = await self._shorturls.get_by_id(ShortURLID(id))
        if shorturl is None or shorturl.owner_id != user_id:
            return Err(ShortURLNotFoundError())
        return Ok(ShortURLDetails.from_entity(shorturl))
