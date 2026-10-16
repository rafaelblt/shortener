from shortener.domain import Slug
from shortener.domain.errors import ShortURLDeactivatedError
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.clock import Clock
from shortener.use_cases.errors import ShortURLNotFoundError
from shortener.use_cases.resolved_slug import ResolvedSlug
from shortener.use_cases.unit_of_work import UnitOfWork


type ResolveSlugError = ShortURLNotFoundError | ShortURLDeactivatedError


class ResolveSlug:
    def __init__(self, uow: UnitOfWork, clock: Clock):
        self._uow = uow
        self._clock = clock

    async def execute(self, slug: str) -> Result[ResolvedSlug, ResolveSlugError]:
        """
        Raises:
            TypeError: The slug isn't a str.
            ValueError: The slug is empty.
        """
        # parse() and not create(), so a slug created under older rules still
        # resolves.
        parsed_slug = Slug.parse(slug)
        async with self._uow.begin() as transaction:
            shorturl = await transaction.shorturls.get_by_slug(parsed_slug)
            if shorturl is None:
                return Err(ShortURLNotFoundError())
            result = shorturl.resolve(self._clock.now())
            if isinstance(result, Ok):
                # The slug didn't change, so save() can't return SlugTakenError.
                (await transaction.shorturls.save(shorturl)).unwrap()
                await transaction.commit()
            return result.map(ResolvedSlug.from_target_url)
