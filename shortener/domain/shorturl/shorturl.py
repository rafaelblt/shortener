from datetime import datetime, timezone

from typing import Optional

from shortener.domain.shared.datetime_utils import is_utc
from shortener.domain.user import User

from .fields import Slug, URL, ShortURLStatus
from .exceptions import (
    ShortURLAvailabilityError,
    ShortURLExpiredError,
    ShortURLDeactivatedError,
    ShortURLSuspendedError,
    ShortURLBannedError,
    ShortURLAttributeTypeError
)


class ShortURL:

    def __init__(
        self,
        original_url: URL,
        slug: Slug,
        owner: User = None,
        id: Optional[int] = None,
        status: ShortURLStatus = ShortURLStatus.ACTIVE,
        visit_count: int = 0,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        created_at = created_at or datetime.now(tz=timezone.utc)

        self.validate_id(id)
        self.validate_slug(slug)
        self.validate_original_url(original_url)
        self.validate_owner(owner)
        self.validate_status(status)
        self.validate_visit_count(visit_count)
        self.validate_created_at(created_at)
        self.validate_expires_at(expires_at)
        self.validate_last_accessed_at(last_accessed_at)

        self._id = id
        self._slug = slug
        self._original_url = original_url
        self._owner = owner
        self._status = status
        self._visit_count = visit_count
        self._created_at = created_at
        self._expires_at = expires_at
        self._last_accessed_at = last_accessed_at

        self._update_status()


    @property
    def id(self):
        return self._id

    @property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, slug):
        self.validate_slug(slug)
        self._slug = slug

    @property
    def original_url(self):
        return self._original_url
    
    @original_url.setter
    def original_url(self, original_url):
        self.validate_original_url(original_url)
        self._original_url = original_url

    @property
    def owner(self):
        return self._owner

    @property
    def status(self):
        return self._status

    @property
    def visit_count(self):
        return self._visit_count

    @property
    def created_at(self):
        return self._created_at

    @property
    def expires_at(self):
        return self._expires_at

    @property
    def last_accessed_at(self):
        return self._last_accessed_at


    @property
    def is_available(self) -> bool:
        """Returns True if the ShortURL is available to be accessed."""
        return self.status == ShortURLStatus.ACTIVE


    def validate_all(self):
        self.validate_id(self._id)
        self.validate_slug(self._slug)
        self.validate_original_url(self._original_url)
        self.validate_owner(self._owner)
        self.validate_status(self._status)
        self.validate_visit_count(self._visit_count)
        self.validate_created_at(self._created_at)
        self.validate_expires_at(self._expires_at)
        self.validate_last_accessed_at(self._last_accessed_at)

    @staticmethod
    def validate_id(id):
        if not isinstance(id, (int, type(None))):
            raise ShortURLAttributeTypeError(
                attr="id", type_expected="int or None", got=id
            )

    @staticmethod
    def validate_slug(slug):
        if not isinstance(slug, Slug):
            raise ShortURLAttributeTypeError(
                attr="slug", type_expected="Slug", got=slug
            )
        
    @staticmethod
    def validate_original_url(original_url):
        if not isinstance(original_url, URL):
            raise ShortURLAttributeTypeError(
                attr="original_url", type_expected="URL", got=original_url
            )
    
    @staticmethod
    def validate_owner(owner):
        if not isinstance(owner, User):
            raise ShortURLAttributeTypeError(
                attr="owner", type_expected="User", got=owner
            )
    
    @staticmethod
    def validate_status(status):
        if not isinstance(status, ShortURLStatus):
            raise ShortURLAttributeTypeError(
                attr="status", type_expected="ShortURLStatus", got=status
            )
    
    @staticmethod
    def validate_visit_count(visit_count):
        if not isinstance(visit_count, int):
            raise ShortURLAttributeTypeError(
                attr="visit_count", type_expected="int", got=visit_count
            )
        if visit_count < 0:
            raise ValueError(
                ("The ShortURL visit_count must be greater than or equal to 0, "
                f"got {visit_count}")
            )

    @staticmethod
    def validate_created_at(created_at):
        if not isinstance(created_at, datetime):
            raise ShortURLAttributeTypeError(
                attr="created_at", type_expected="datetime", got=created_at
            )
        if not is_utc(created_at):
            raise ValueError(
                "The ShortURL created_at must be in UTC timezone."
            )

    @staticmethod
    def validate_expires_at(expires_at):
        if not isinstance(expires_at, (datetime, type(None))):
            raise ShortURLAttributeTypeError(
                attr="expires_at", type_expected="datetime or None", got=expires_at
            )
        if isinstance(expires_at, datetime) and not is_utc(expires_at):            
            raise ValueError(
                "The ShortURL expires_at must be in UTC timezone."
            )

    @staticmethod
    def validate_last_accessed_at(last_accessed_at):
        if not isinstance(last_accessed_at, (datetime, type(None))):
            raise ShortURLAttributeTypeError(
                attr="last_accessed_at", 
                type_expected="datetime or None", 
                got=last_accessed_at
            )
        if isinstance(last_accessed_at, datetime) and not is_utc(last_accessed_at):
            raise ValueError(
                "The ShortURL last_accessed_at must be in UTC timezone."
            )


    def change_owner(self, new_owner: User):
        self.validate_owner(new_owner)
        self._owner = new_owner

    def record_visit(self):
        """
        Registers a new visit to the ShortURL.
        Increments the visit count and updates the last accessed timestamp.
        """
        self._visit_count = self.visit_count + 1
        self._last_accessed_at = datetime.now(tz=timezone.utc)
    
    def resolve(self) -> URL:
        """
        Returns the original_url if the ShortURL is available to be resolved.

        Raises:
            ShortURLSuspendedError: If the ShortURL status is SUSPENDED.
            ShortURLDeactivatedError: If the ShortURL status is DEACTIVATED.
            ShortURLExpiredError: If the ShortURL status is EXPIRED.
            ShortURLBannedError: If the ShortURL status is BANNED.
        """
        if self.status == ShortURLStatus.ACTIVE:
            return self.original_url
        elif self.status == ShortURLStatus.SUSPENDED:
            raise ShortURLSuspendedError()
        elif self.status == ShortURLStatus.DEACTIVATED:
            raise ShortURLDeactivatedError()
        elif self.status == ShortURLStatus.EXPIRED:
            raise ShortURLExpiredError()
        elif self.status == ShortURLStatus.BANNED:
            raise ShortURLBannedError()
        else:
            ShortURLAvailabilityError()

    def enable(self):
        if self.status == ShortURLStatus.DEACTIVATED:
            self._status = ShortURLStatus.ACTIVE
            return

        if self.status == ShortURLStatus.SUSPENDED:
            raise ShortURLSuspendedError()
        elif self.status == ShortURLStatus.EXPIRED:
            raise ShortURLExpiredError()
        elif self.status == ShortURLStatus.BANNED:
            raise ShortURLBannedError()
        
    def disable(self):
        if self.status == ShortURLStatus.ACTIVE:
            self._status = ShortURLStatus.DEACTIVATED
            return

        if self.status == ShortURLStatus.SUSPENDED:
            raise ShortURLSuspendedError()
        if self.status == ShortURLStatus.EXPIRED:
            raise ShortURLExpiredError()
        if self.status == ShortURLStatus.BANNED:
            raise ShortURLBannedError()

    def _update_status(self):
        if self.status == ShortURLStatus.ACTIVE and self._check_expiration():
            self._status = ShortURLStatus.EXPIRED

    def _check_expiration(self):
        return (
            isinstance(self.expires_at, datetime) and
            self.expires_at <= datetime.now(tz=timezone.utc)
        )


    def __repr__(self):
        return (
            f"<ShortURL(id={self.id}, slug={self.slug}, original_url={self.original_url}, "
            f"owner={self.owner}, status={self.status}, visit_count={self.visit_count}, "
            f"created_at={self.created_at}, expires_at={self.expires_at}, "
            f"last_accessed_at={self.last_accessed_at})>"
        )
