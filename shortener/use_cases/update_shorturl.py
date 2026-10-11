from uuid import UUID

from shortener.domain import ShortURLID, Slug, TargetURL, UserID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import (
    InvalidInputError,
    NotAuthenticatedError,
    NothingToUpdateError,
    ShortURLNotFoundError,
    collect_field_errors,
)
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import SlugTakenError
from shortener.use_cases.unit_of_work import UnitOfWork


type UpdateShortURLError = (
    NotAuthenticatedError
    | NothingToUpdateError
    | InvalidInputError
    | ShortURLNotFoundError
    | SlugTakenError
)


class UpdateShortURL:

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):
        self._uow = uow
        self._current_user = current_user

    async def execute(
        self, id: UUID, target_url: str | None = None, slug: str | None = None
    ) -> Result[ShortURLDetails, UpdateShortURLError]:
        """
        Changes only the values that aren't None.

        Raises:
            TypeError: The id isn't a UUID.
        """
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())
        if target_url is None and slug is None:
            return Err(NothingToUpdateError())

        target_url_result = (
            TargetURL.create(target_url) if target_url is not None else Ok(None)
        )
        slug_result = Slug.create(slug) if slug is not None else Ok(None)
        if field_errors := collect_field_errors(
            target_url=target_url_result, slug=slug_result
        ):
            return Err(InvalidInputError(field_errors))

        return await self._update(
            ShortURLID(id), target_url_result.unwrap(), slug_result.unwrap(), user_id
        )

    async def _update(
        self,
        id: ShortURLID,
        target_url: TargetURL | None,
        slug: Slug | None,
        user_id: UserID,
    ) -> Result[ShortURLDetails, ShortURLNotFoundError | SlugTakenError]:
        async with self._uow.begin() as transaction:
            shorturl = await transaction.shorturls.get_by_id(id)
            if shorturl is None or shorturl.owner_id != user_id:
                return Err(ShortURLNotFoundError())
            if target_url is not None:
                shorturl.change_target_url(target_url)
            if slug is not None:
                shorturl.change_slug(slug)
            saved = await transaction.shorturls.save(shorturl)
            if isinstance(saved, Err):
                return saved
            await transaction.commit()
            return Ok(ShortURLDetails.from_entity(shorturl))
