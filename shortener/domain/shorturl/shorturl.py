from datetime import datetime, timezone

from typing import Optional

from shortener.domain.shared.datetime_utils import is_utc

from .slug import Slug
from .url import URL
from .exceptions import ShortURLExpiredError, ShortURLInactiveError, ShortURLInvalidDatetimeTimezone


class ShortURL:

    def __init__(
        self,
        original_url: URL,
        slug: Slug = None,
        id: Optional[int] = None,
        owner_id: Optional[int] = None,
        is_active: bool = True,
        visit_count: int = 0,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        """
        Args:
            id (Optional[int]): The unique identifier of the ShortURL. 
                Defaults to None.
            original_url (URL): The original URL being shortened.
            slug (Slug): The slug used to shorten the URL.
            owner_id (Optional[int]): The ID of the owner of the ShortURL.
                Defaults to None.
            is_active (bool): Indicates whether the ShortURL is active.
                Defaults to True.
            visit_count (int): The number of times the ShortURL has been visited.
                Defaults to 0.
            created_at (Optional[datetime]): The timestamp when the ShortURL was
                created. Defaults to the current UTC time.
            expires_at (Optional[datetime]): The timestamp when the ShortURL
                will expire. Defaults to None.
            last_accessed_at (Optional[datetime]): The timestamp when the ShortURL
                was last accessed. Defaults to None.
        
        Raises:
            TypeError: If any field has invalid type.
            ValueError: If any field has invalid value.
        """
        created_at = created_at or datetime.now(tz=timezone.utc)

        self.validate_id(id)
        self.validate_slug(slug)
        self.validate_original_url(original_url)
        self.validate_owner_id(owner_id)
        self.validate_is_active(is_active)
        self.validate_visit_count(visit_count)
        self.validate_created_at(created_at)
        self.validate_expires_at(expires_at)
        self.validate_last_accessed_at(last_accessed_at)

        self._id = id
        self._slug = slug
        self._original_url = original_url
        self._owner_id = owner_id
        self._is_active = is_active
        self._visit_count = visit_count
        self._created_at = created_at
        self._expires_at = expires_at
        self._last_accessed_at = last_accessed_at


    @property
    def id(self) -> int:
        return self._id

    @property
    def slug(self) -> Slug:
        return self._slug

    @slug.setter
    def slug(self, slug):
        self.validate_slug(slug)
        self._slug = slug

    @property
    def original_url(self) -> URL:
        return self._original_url
    
    @original_url.setter
    def original_url(self, original_url):
        self.validate_original_url(original_url)
        self._original_url = original_url

    @property
    def owner_id(self) -> int:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        self.validate_owner_id(owner_id)
        self._owner_id = owner_id

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def visit_count(self) -> int:
        return self._visit_count

    @visit_count.setter
    def visit_count(self, visit_count):
        self.validate_visit_count(visit_count)
        self._visit_count = visit_count

    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @created_at.setter
    def created_at(self, created_at):
        self.validate_created_at(created_at)
        self._created_at = created_at

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @expires_at.setter
    def expires_at(self, expires_at):
        self.validate_expires_at(expires_at)
        self._expires_at = expires_at

    @property
    def last_accessed_at(self) -> datetime:
        return self._last_accessed_at
    
    @last_accessed_at.setter
    def last_accessed_at(self, last_accessed_at):
        self.validate_last_accessed_at(last_accessed_at)
        self._last_accessed_at = last_accessed_at


    @property
    def is_expired(self) -> bool:
        """Checks if the ShortURL is expired."""
        return (
            isinstance(self.expires_at, datetime) and
            self.expires_at <= datetime.now(tz=timezone.utc)
        )

    @property
    def is_available(self) -> bool:
        """Returns True if the ShortURL is available to be accessed."""
        try:
            self.resolve()
        except:
            return False
        return True

    def validate_all(self):
        self.validate_id(self._id)
        self.validate_slug(self._slug)
        self.validate_original_url(self._original_url)
        self.validate_owner_id(self._owner_id)
        self.validate_is_active(self._is_active)
        self.validate_visit_count(self._visit_count)
        self.validate_created_at(self._created_at)
        self.validate_expires_at(self._expires_at)
        self.validate_last_accessed_at(self._last_accessed_at)

    @staticmethod
    def validate_id(id):
        if not isinstance(id, (int, type(None))):
            raise TypeError(
                ("The ShortURL id must be int or None, not "
                f"{type(id).__name__}")
            )

    @staticmethod
    def validate_slug(slug):
        if not isinstance(slug, Slug):
            raise TypeError(
                ("The ShortURL slug must be an instance of Slug, not "
                f"{type(slug).__name__}")
            )
        
    @staticmethod
    def validate_original_url(original_url):
        if not isinstance(original_url, URL):
            raise TypeError(
                ("The ShortURL original_url must be an instance of URL, not "
                f"{type(original_url).__name__}")
            )
    
    @staticmethod
    def validate_owner_id(owner_id):
        if not isinstance(owner_id, (int, type(None))):
            raise TypeError(
                ("The ShortURL owner_id must be int or None, not "
                f"{type(owner_id).__name__}")
            )
    
    @staticmethod
    def validate_is_active(is_active):
        if not isinstance(is_active, bool):
            raise TypeError(
                ("The ShortURL is_active must be bool, not "
                f"{type(is_active).__name__}")
            )
    
    @staticmethod
    def validate_visit_count(visit_count):
        if not isinstance(visit_count, int):
            raise TypeError(
                ("The ShortURL visit_count must be int, not "
                f"{type(visit_count).__name__}")
            )
        if visit_count < 0:
            raise ValueError(
                ("The ShortURL visit_count must be greater than or equal to 0, "
                f"got {visit_count}")
            )

    @staticmethod
    def validate_created_at(created_at):
        if not isinstance(created_at, datetime):
            raise TypeError(
                ("The ShortURL created_at must be an instance of datetime, "
                f"not {type(created_at).__name__}")
            )
        if not is_utc(created_at):
            raise ShortURLInvalidDatetimeTimezone(
                "The ShortURL created_at must be in UTC timezone."
            )

    @staticmethod
    def validate_expires_at(expires_at):
        if not isinstance(expires_at, (datetime, type(None))):
            raise TypeError(
                ("The ShortURL expires_at must be an instance of datetime "
                f"or None, not {type(expires_at).__name__}")
            )
        if isinstance(expires_at, datetime) and not is_utc(expires_at):            
            raise ShortURLInvalidDatetimeTimezone(
                "The ShortURL expires_at must be in UTC timezone."
            )

    @staticmethod
    def validate_last_accessed_at(last_accessed_at):
        if not isinstance(last_accessed_at, (datetime, type(None))):
            raise TypeError(
                ("The ShortURL last_accessed_at must be an instance of datetime "
                f"or None, not {type(last_accessed_at).__name__}")
            )
        if isinstance(last_accessed_at, datetime) and not is_utc(last_accessed_at):
            raise ShortURLInvalidDatetimeTimezone(
                "The ShortURL last_accessed_at must be in UTC timezone."
            )


    def record_visit(self):
        """
        Registers a new visit to the ShortURL.
        Increments the visit count and updates the last accessed timestamp.
        """
        self.visit_count = self.visit_count + 1
        self.last_accessed_at = datetime.now(tz=timezone.utc)
    
    def resolve(self) -> URL:
        """
        Returns the original_url if the ShortURL is available to be resolved.
        """
        if not self.is_active:
            raise ShortURLInactiveError()
        if self.is_expired:
            raise ShortURLExpiredError()
        return self.original_url

    def _disable(self):
        """
        Disables the ShortURL by setting is_active to False.
        """
        self._is_active = False

    def _enable(self):
        """
        Enables the ShortURL by setting is_active to True.
        """
        self._is_active = True


    def __repr__(self):
        return (
            f"<ShortURL(id={self.id}, slug={self.slug}, original_url={self.original_url}, "
            f"owner_id={self.owner_id}, is_active={self.is_active}, visit_count={self.visit_count}, "
            f"created_at={self.created_at}, expires_at={self.expires_at}, "
            f"last_accessed_at={self.last_accessed_at})>"
        )
