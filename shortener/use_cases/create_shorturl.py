from datetime import datetime
from typing import Final

from shortener.domain import ShortURL, Slug, TargetURL, UserID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.clock import Clock
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import (
    InvalidInputError,
    NotAuthenticatedError,
    collect_field_errors,
)
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import ShortURLRepository, SlugTakenError
from shortener.use_cases.unit_of_work import UnitOfWork


MAX_GENERATED_SLUG_ATTEMPTS: Final = 10

type CreateShortURLError = NotAuthenticatedError | InvalidInputError | SlugTakenError


class CreateShortURL:

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser, clock: Clock):
        self._uow = uow
        self._current_user = current_user
        self._clock = clock

    async def execute(
        self, target_url: str, slug: str | None = None
    ) -> Result[ShortURLDetails, CreateShortURLError]:
        """
        Generates the slug when it is None.

        Raises:
            RuntimeError: Every generated slug was taken.
        """
        user_id = await self._current_user.get_id()
        if user_id is None:
            return Err(NotAuthenticatedError())

        target_url_result = TargetURL.create(target_url)
        slug_result = Slug.create(slug) if slug is not None else Ok(None)
        if field_errors := collect_field_errors(
            target_url=target_url_result, slug=slug_result
        ):
            return Err(InvalidInputError(field_errors))

        return await self._create(
            target_url_result.unwrap(), slug_result.unwrap(), user_id
        )

    async def _create(
        self, target_url: TargetURL, slug: Slug | None, owner_id: UserID
    ) -> Result[ShortURLDetails, SlugTakenError]:
        now = self._clock.now()
        async with self._uow.begin() as transaction:
            if slug is None:
                shorturl = await _add_with_a_generated_slug(
                    transaction.shorturls, target_url, owner_id, now
                )
            else:
                shorturl = ShortURL.create(
                    slug=slug, target_url=target_url, owner_id=owner_id, now=now
                )
                added = await transaction.shorturls.add(shorturl)
                if isinstance(added, Err):
                    return added
            await transaction.commit()
            return Ok(ShortURLDetails.from_entity(shorturl))


async def _add_with_a_generated_slug(
    shorturls: ShortURLRepository,
    target_url: TargetURL,
    owner_id: UserID,
    now: datetime,
) -> ShortURL:
    for _ in range(MAX_GENERATED_SLUG_ATTEMPTS):
        shorturl = ShortURL.create(
            slug=Slug.generate(), target_url=target_url, owner_id=owner_id, now=now
        )
        if isinstance(await shorturls.add(shorturl), Ok):
            return shorturl
    raise RuntimeError(
        f"Every generated slug was taken, after {MAX_GENERATED_SLUG_ATTEMPTS} attempts"
    )
