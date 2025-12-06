from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.shorturl.exceptions import ShortURLNotFoundError
from shortener.domain.shorturl.shorturl import ShortURL

from shortener.domain.user import UserRepository
from shortener.domain.user.exceptions import UserNotFoundError


class ReadShortURLOfUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    async def execute(
        self,
        user_pk: PrimaryKey,
        shorturl_pk: PrimaryKey,
    ) -> ShortURL:
        user = await self.user_repo.get_by_pk(user_pk)
        if user is None:
            raise UserNotFoundError(value=user_pk, field="pk")
            
        shorturl = await user.shorturls.get_by_pk(shorturl_pk)
        if shorturl is None:
            raise ShortURLNotFoundError(value=shorturl_pk, field="pk")

        return shorturl
