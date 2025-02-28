from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from shortener.domain.shorturl import ShortURL, ShortURLRepository

from shortener.infrastructure.db.models import ShortURLModel


class SQLAlchemyShortURLRepository(ShortURLRepository):
    """
    SQLAlchemy implementation of ShortURLRepository.
    """

    def __init__(self, session: Session):
        """
        Args:
            session (Session): SQLAlchemy session instance.
        """
        self.session = session

    def get_by_slug(self, slug: str) -> ShortURL | None:
        """
        Retrieves a ShortURL by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            Optional[ShortURL]: The ShortURL domain object, or None if not found.
        """
        try:
            model = self.session.query(ShortURLModel).filter_by(slug=slug).one()
            return self._to_domain(model)
        except NoResultFound:
            return None
        
    def exists_by_slug(self, slug: str) -> bool:
        """
        Checks if a ShortURL exists by its slug.

        Args:
            slug (str): The ShortURL slug.

        Returns:
            bool: True if a ShortURL with the given slug exists, False otherwise.
        """    
        return self.get_by_slug(slug) is not None

    def save(self, shorturl: ShortURL) -> None:
        """
        Saves a ShortURL object to the database.

        Args:
            shorturl (ShortURL): The ShortURL domain object.
        """
        shorturl_model = self._to_model(shorturl)
        self.session.add(shorturl_model)
        self.session.commit()

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
