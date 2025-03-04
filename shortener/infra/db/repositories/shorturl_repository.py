from sqlalchemy import select
from sqlalchemy.orm import Session

from shortener.domain.shorturl import ShortURL, ShortURLRepository

from shortener.infra.db.models import ShortURLModel


class SQLAlchemyShortURLRepository(ShortURLRepository):
    """SQLAlchemy implementation of ShortURLRepository."""

    def __init__(self, session: Session):
        """
        Initializes the repository with a SQLAlchemy Session instance.

        Args:
            session (Session): SQLAlchemy Session instance.
        """
        self.session = session

    def get_by_id(self, id: int) -> ShortURL | None:
        """
        Retrieves a ShortURL by its id.

        Args:
            id (int): The ShortURL id.

        Returns:
            ShortURL: The ShortURL domain object.
            None: If no ShortURL with the given id is found
        """
        model = self._get_model_by_id(id)
        return self._to_domain(model) if model else None

    def get_by_slug(self, slug: str) -> ShortURL | None:
        """
        Retrieves a ShortURL by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            ShortURL: The ShortURL domain object.
            None: If no ShortURL with the given slug is found.
        """
        model = self._get_model_by_slug(slug)
        return self._to_domain(model) if model else None
        
    def exists_by_slug(self, slug: str) -> bool:
        """
        Checks if a ShortURL exists by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            bool: True if a ShortURL with the given slug exists, False otherwise.
        """    
        return self._get_model_by_slug(slug) is not None

    def save(self, shorturl: ShortURL) -> ShortURL:
        """
        Saves a ShortURL object to the database and return the updated object.

        Args:
            shorturl (ShortURL): The ShortURL domain object.

        Returns:
            ShortURL: Return the domain object with id attr updated.
        """
        shorturl_model = self._to_model(shorturl)
        self.session.add(shorturl_model)
        self.session.commit()
        return self._to_domain(shorturl_model)

    def delete_by_id(self, id: int) -> ShortURL:
        """
        Deletes a ShortURL object from the database.

        Args:
            id (int): The ShortURL id.

        Returns:
            ShortURL: The ShortURL domain object that was deleted.
        """
        shorturl_model = self._get_model_by_id(id)
        self.session.delete(shorturl_model)
        self.session.commit()
        return self._to_domain(shorturl_model)

    def _get_model_by_id(self, id: int) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its id.

        Args:
            id (int): The ShortURLModel id.

        Returns:
            ShortURLModel: The ShortURLModel object.
            None: If no ShortURL with the given id is found.
        """
        model = self.session.get(ShortURLModel, id)
        return model or None

    def _get_model_by_slug(self, slug: str) -> ShortURLModel | None:
        """
        Retrieves a ShortURLModel by its slug.

        Args:
            slug (str): The ShortURLModel slug.

        Returns:
            ShortURLModel: The ShortURLModel object.
            None: If no ShortURL with the given slug is found.
        """
        model = self.session.scalar(
            select(ShortURLModel).where(ShortURLModel.slug == slug)
        )
        return model

    def _to_domain(self, model: ShortURLModel) -> ShortURL:
        """
        Converts a SQLAlchemy model instance to a domain entity.
        """
        return ShortURL(
            id=model.id,
            slug=model.slug,
            original_url=model.original_url,
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
