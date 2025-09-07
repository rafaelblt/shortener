from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl import ShortURL
from shortener.domain.shorturl.fields.slug import Slug
from shortener.domain.user.fields import ShortURLCollection

from shortener.infra.db.mappers.shorturl import map_shorturl_model_to_domain
from shortener.infra.db.models import UserModel, ShortURLModel


class SQLAlchemyShortURLCollection(ShortURLCollection):

    def __init__(self, session: AsyncSession, user_id: int):
        self._session = session
        self._user_id = user_id

    async def get_all(self) -> list[ShortURL]:
        stmt = select(ShortURLModel).where(ShortURLModel.owner_id == self._user_id)
        result = await self._session.execute(stmt)
        shorturls_model = result.scalars().all()
        return [map_shorturl_model_to_domain(s) for s in shorturls_model]
    
    async def get_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        shorturl_model = await self._get_user_shorturl_by_id(pk.get_id())
        if shorturl_model is None:
            return None
        return map_shorturl_model_to_domain(shorturl_model)
    
    async def get_by_slug(self, slug: Slug) -> ShortURL | None:
        stmt = (
            select(ShortURLModel)
            .where(
                ShortURLModel.slug == slug,
                ShortURLModel.owner_id == self._user_id,
            )
        )
        result = await self._session.execute(stmt)
        shorturl_model = result.scalar_one_or_none()
        if shorturl_model is None:
            return None
        return map_shorturl_model_to_domain(shorturl_model)
    
    async def add(self, shorturl: ShortURL) -> None:
        shorturl_model = await self._session.get(ShortURLModel, shorturl.pk.get_id())
        if shorturl_model is None:
            raise ValueError(f"ShortURL with pk={shorturl.pk} was not found")
        shorturl_model.owner_id = self._user_id
        await self._session.commit()

    async def remove_by_pk(self, pk: PrimaryKey) -> ShortURL | None:
        shorturl_model = await self._get_user_shorturl_by_id(pk.get_id())
        if shorturl_model is None:
            return None
        shorturl_model.owner_id = None
        await self._session.commit()
        await self._session.refresh(shorturl_model)
        return map_shorturl_model_to_domain(shorturl_model)
    
    async def count(self) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(ShortURLModel)
            .where(ShortURLModel.owner_id == self._user_id)
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return count

    async def _get_user_model(self):
        user = await self._session.get(UserModel, self._user_id)
        if user is None:
            raise ValueError(f"User with id={self._user_id} was not found")
        return user
    
    async def _get_user_shorturl_by_id(self, shorturl_id):
        stmt = (
            select(ShortURLModel)
            .where(
                ShortURLModel.id == shorturl_id,
                ShortURLModel.owner_id == self._user_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
