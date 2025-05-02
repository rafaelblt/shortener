from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared import PaginatedResult
from shortener.domain.shorturl import ShortURL, ShortURLRepository
from shortener.domain.shorturl.exceptions import ShortURLNotFoundInDatabaseError

from shortener.infra.db.mappers import (
    map_shorturl_model_to_domain, map_shorturl_domain_to_model
)
from shortener.infra.db.models import ShortURLModel


class SQLAlchemyShortURLRepository(ShortURLRepository):
    """SQLAlchemy implementation of ShortURLRepository."""

    def __init__(self, session: AsyncSession):
        """
        Args:
            session (Session): SQLAlchemy Async Session instance.
        """
        self.session = session

    async def add(self, shorturl: ShortURL) -> ShortURL:
        shorturl_model = self._to_model(shorturl)
        self.session.add(shorturl_model)
        await self.session.commit()
        await self.session.refresh(shorturl_model)
        return self._to_domain(shorturl_model)
    
    async def update(self, shorturl: ShortURL) -> ShortURL:
        existing_model = await self._get_model_by_id(shorturl.id)
        if existing_model is None:
            raise ShortURLNotFoundInDatabaseError(
                f"ShortURL with id={shorturl.id} not found in database."
            )

        existing_model.slug = shorturl.slug
        existing_model.original_url = shorturl.original_url
        existing_model.owner_id = shorturl.owner.id
        existing_model.status = shorturl.status
        existing_model.visit_count = shorturl.visit_count
        existing_model.created_at = shorturl.created_at
        existing_model.expires_at = shorturl.expires_at
        existing_model.last_accessed_at = shorturl.last_accessed_at

        await self.session.commit()
        await self.session.refresh(existing_model)

        return self._to_domain(existing_model)

    async def get_all(self) -> list[ShortURL]:
        models = await self._get_all_models()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, id: int) -> ShortURL | None:
        model = await self._get_model_by_id(id)
        return self._to_domain(model) if model else None

    async def get_by_slug(self, slug: str) -> ShortURL | None:
        model = await self._get_model_by_slug(slug)
        return self._to_domain(model) if model else None

    async def list_paginated(self, offset: int, limit: int):
        total = await self.session.scalar(
            select(func.count()).select_from(ShortURLModel)
        )
        rows = await self.session.scalars(
            select(ShortURLModel)
            .offset(offset)
            .limit(limit)
        )
        entities = [self._to_domain(m) for m in rows.all()]
        return PaginatedResult(entities, total, offset, limit)
        
    async def exists_by_slug(self, slug: str) -> bool:
        model = await self._get_model_by_slug(slug)
        return model is not None

    async def delete_by_id(self, id: int) -> ShortURL:
        model = await self._get_model_by_id(id)
        if model is None:
            raise ShortURLNotFoundInDatabaseError(
                f"ShortURL with id={id} not found in database."
            )
        
        domain = self._to_domain(model)
        
        await self.session.delete(model)
        await self.session.commit()
        return domain

    async def _get_all_models(self) -> Sequence[ShortURLModel]:
        result = await self.session.scalars(select(ShortURLModel))
        return result.all()

    async def _get_model_by_id(self, id: int) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its id.

        Args:
            id (int): The ShortURLModel id.

        Returns:
            Optional[ShortURLModel]: The model object or None if not found.
        """
        stmt = select(ShortURLModel).where(ShortURLModel.id == id)
        model = await self.session.scalar(stmt)
        return model

    async def _get_model_by_slug(self, slug: str) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its slug.

        Args:
            slug (str): The ShortURLModel slug.

        Returns:
            Optional[ShortURLModel]: The model object or None if not found.
        """
        model = await self.session.scalar(
            select(ShortURLModel).where(ShortURLModel.slug == slug)
        )
        return model

    def _to_domain(self, model: ShortURLModel) -> ShortURL:
        """Convets a SQLAlchemy model instance to a domain entity."""
        return map_shorturl_model_to_domain(model)
    
    def _to_model(self, entity: ShortURL) -> ShortURLModel:
        """Converts a domain entity to a SQLAlchemy model instance."""
        return map_shorturl_domain_to_model(entity)
