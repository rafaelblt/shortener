from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared import PaginatedResult
from shortener.domain.shorturl import ShortURL, ShortURLRepository, Slug, URL
from shortener.domain.shorturl.exceptions import (
    ShortURLNotFoundInDatabase, ShortURLInvalidToUpdate
)

from shortener.infra.db.models import ShortURLModel


class SQLAlchemyShortURLRepository(ShortURLRepository):
    """SQLAlchemy implementation of ShortURLRepository."""

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a SQLAlchemy Session instance.

        Args:
            session (Session): SQLAlchemy Session instance.
        """
        self.session = session

    async def get_all(self) -> list[ShortURL]:
        models = await self._get_all_models()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, id: int) -> ShortURL | None:
        """
        Retrieves a ShortURL by its id.

        Args:
            id (int): The ShortURL id.

        Returns:
            Optional[ShortURL]: The ShortURL domain object or None if not found.
        """
        model = await self._get_model_by_id(id)
        return self._to_domain(model) if model else None

    async def get_by_slug(self, slug: str) -> ShortURL | None:
        """
        Retrieves a ShortURL by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            Optional[ShortURL]: The ShortURL domain object or None if not found.
        """
        model = await self._get_model_by_slug(slug)
        return self._to_domain(model) if model else None
        
    async def exists_by_slug(self, slug: str) -> bool:
        """
        Checks if a ShortURL exists by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            bool: True if a ShortURL with the given slug exists, False otherwise.
        """
        model = await self._get_model_by_slug(slug)
        return model is not None

    async def save(self, shorturl: ShortURL) -> ShortURL:
        """
        Saves a ShortURL object to the database and return the updated object.

        Args:
            shorturl (ShortURL): The ShortURL domain object.

        Returns:
            ShortURL: Return the domain object with id attr updated.
        """
        shorturl_model = self._to_model(shorturl)
        self.session.add(shorturl_model)
        await self.session.commit()
        await self.session.refresh(shorturl_model)
        return self._to_domain(shorturl_model)

    async def delete_by_id(self, id: int) -> ShortURL:
        """
        Deletes a ShortURL object from the database.

        Args:
            id (int): The ShortURL id.

        Returns:
            ShortURL: The ShortURL domain object that was deleted.
        """
        shorturl_model = await self._get_model_by_id(id)
        await self.session.delete(shorturl_model)
        await self.session.commit()
        return self._to_domain(shorturl_model)

    async def _get_all_models(self) -> list[ShortURLModel]:
        result = await self.session.scalars(select(ShortURLModel))
        return result.all()

    async def _get_model_by_id(self, id: int) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its id.

        Args:
            id (int): The ShortURLModel id.

        Returns:
            Optional[ShortURLModel]: The ShortURLModel object or None if not found.
        """
        model = await self.session.get(ShortURLModel, id)
        return model

    async def _get_model_by_slug(self, slug: str) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its slug.

        Args:
            slug (str): The ShortURLModel slug.

        Returns:
            Optional[ShortURLModel]: The ShortURLModel object or None if not found.
        """
        model = await self.session.scalar(
            select(ShortURLModel).where(ShortURLModel.slug == slug)
        )
        return model

    def _to_domain(self, model: ShortURLModel) -> ShortURL:
        """
        Converts a SQLAlchemy model instance to a domain entity.
        """
        return ShortURL(
            id=model.id,
            slug=Slug(model.slug),
            original_url=URL(model.original_url),
            is_active=model.is_active,
            visit_count=model.visit_count,
            created_at=model.created_at,
            expires_at=model.expires_at,
            last_accessed_at=model.last_accessed_at,
        )
    
    def _to_model(self, entity: ShortURL) -> ShortURLModel:
        """
        Converts a domain entity to a SQLAlchemy model instance.
        """
        return ShortURLModel(
            id=entity.id,
            slug=entity.slug,
            original_url=entity.original_url,
            is_active=entity.is_active,
            visit_count=entity.visit_count,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_accessed_at=entity.last_accessed_at,
        )
