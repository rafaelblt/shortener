from typing import Optional

from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.user import User, UserRepository

from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError
from shortener.domain.shorturl.fields import Slug, URL
from shortener.domain.shorturl.utils import generate_unique_slug
from shortener.domain.user.exceptions import UserNotFoundError


class CreateShortURLForUserUseCase:
    """Use case to create a new ShortURL for a User."""

    def __init__(
        self,
        shorturl_repository: ShortURLRepository,
        user_repository: UserRepository
    ):
        self.shorturl_repo = shorturl_repository
        self.user_repo = user_repository

    async def execute(
        self, 
        original_url: URL,
        owner_pk: PrimaryKey,
        custom_slug: Optional[Slug] = None,
    ) -> ShortURL:
        """
        Executes the Use Case with the provided data.

        Args:
            original_url (URL): The original_url to be shortened.
            owner_pk (PrimaryKey): Owner PK of the ShortURL.
            custom_slug (Optional[Slug]): Custom slug of the ShortURL. Will be 
                generated if not provided.

        Returns:
            ShortURL: The entity object created.

        Raises:
            UserNotFoundError: No user found with the given owner_pk.
            ShortURLSlugAlreadyExistsError: If the given custom_slug already 
                exists.
            ShortURLLimitReachedError: If the owner shorturl limit has reached.
        """
        owner = await self._get_owner(owner_pk)
        if custom_slug:
            await self._validate_slug_already_exists(custom_slug)
        else:
            custom_slug = await generate_unique_slug(self.shorturl_repo)

        shorturl = ShortURL(
            slug=custom_slug,
            original_url=original_url,
        )

        shorturl = await self.shorturl_repo.add(shorturl)
        await owner.add_shorturl(shorturl)
        
        return shorturl

    async def _get_owner(self, owner_pk: PrimaryKey) -> User:
        user = await self.user_repo.get_by_pk(owner_pk)
        if user is None:
            raise UserNotFoundError(value=owner_pk, field="pk")
        return user

    async def _validate_slug_already_exists(self, slug: Slug) -> None:
        if await self.shorturl_repo.exists_by_slug(slug):
            raise ShortURLSlugAlreadyExistsError(slug)

