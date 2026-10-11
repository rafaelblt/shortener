from uuid import UUID

from shortener.domain import ShortURLID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from shortener.use_cases.unit_of_work import UnitOfWork


type DeleteShortURLError = NotAuthenticatedError | ShortURLNotFoundError


class DeleteShortURL:

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):
        self._uow = uow
        self._current_user = current_user

    async def execute(self, id: UUID) -> Result[None, DeleteShortURLError]:
        """
        Raises:
            TypeError: The id isn't a UUID.
        """
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())
        shorturl_id = ShortURLID(id)
        async with self._uow.begin() as transaction:
            shorturl = await transaction.shorturls.get_by_id(shorturl_id)
            if shorturl is None or shorturl.owner_id != user_id:
                return Err(ShortURLNotFoundError())
            await transaction.shorturls.remove(shorturl)
            await transaction.commit()
            return Ok(None)
