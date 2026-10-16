from uuid import UUID

from shortener.domain import ShortURLID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import NotAuthenticatedError, ShortURLNotFoundError
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.unit_of_work import UnitOfWork


type EnableShortURLError = NotAuthenticatedError | ShortURLNotFoundError


class EnableShortURL:
    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):
        self._uow = uow
        self._current_user = current_user

    async def execute(self, id: UUID) -> Result[ShortURLDetails, EnableShortURLError]:
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
            shorturl.enable()
            # The slug didn't change, so save() can't return SlugTakenError.
            (await transaction.shorturls.save(shorturl)).unwrap()
            await transaction.commit()
            return Ok(ShortURLDetails.from_entity(shorturl))
