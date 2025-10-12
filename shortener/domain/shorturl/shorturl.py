from typing import Optional

from datetime import datetime, timezone

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.datetime_utils import is_utc
from shortener.domain.shared.valueobjects.url import URL

from .fields import Slug, OriginalURL, ShortURLStatus
from .exceptions import (
    ShortURLAvailabilityError,
    ShortURLExpiredError,
    ShortURLDeactivatedError,
    ShortURLSuspendedError,
    ShortURLBannedError,
    ShortURLAttributeTypeError
)


class ShortURL(DomainEntity):

    @staticmethod
    def get_fields() -> list[str]:
        return [
            "pk",
            "slug",
            "original_url",
            "owner_pk",
            "status",
            "visit_count",
            "created_at",
            "expires_at",
            "last_accessed_at",
        ]

    def __init__(
        self,
        original_url: OriginalURL,
        slug: Slug,
        pk: Optional[PrimaryKey] = None,
        owner_pk: Optional[PrimaryKey] = None,
        status: ShortURLStatus = ShortURLStatus.ACTIVE,
        visit_count: int = 0,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        pk = pk or PrimaryKey.create_pk_undefined()
        owner_pk = owner_pk or PrimaryKey.create_pk_undefined()
        created_at = created_at or datetime.now(tz=timezone.utc)

        self.validate_pk(pk)
        self.validate_slug(slug)
        self.validate_original_url(original_url)
        self.validate_owner_pk(owner_pk)
        self.validate_status(status)
        self.validate_visit_count(visit_count)
        self.validate_created_at(created_at)
        self.validate_expires_at(expires_at)
        self.validate_last_accessed_at(last_accessed_at)

        self._pk = pk
        self._slug = slug
        self._original_url = original_url
        self._owner_pk = owner_pk
        self._status = status
        self._visit_count = visit_count
        self._created_at = created_at
        self._expires_at = expires_at
        self._last_accessed_at = last_accessed_at

        self._update_status()


    @property
    def pk(self):
        return self._pk

    @property
    def slug(self):
        return self._slug

    @property
    def original_url(self):
        return self._original_url

    @property
    def owner_pk(self):
        return self._owner_pk

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


    @staticmethod
    def validate_pk(pk):
        if not isinstance(pk, PrimaryKey):
            raise ShortURLAttributeTypeError(
                attr="pk", type_expected="PrimaryKey", got=pk
            )

    @staticmethod
    def validate_slug(slug):
        if not isinstance(slug, Slug):
            raise ShortURLAttributeTypeError(
                attr="slug", type_expected="Slug", got=slug
            )

    @staticmethod
    def validate_original_url(original_url):
        if not isinstance(original_url, OriginalURL):
            raise ShortURLAttributeTypeError(
                attr="original_url", type_expected="OriginalURL", got=original_url
            )

    @staticmethod
    def validate_owner_pk(owner_pk):
        if not isinstance(owner_pk, PrimaryKey):
            raise ShortURLAttributeTypeError(
                attr="owner_pk", type_expected="PrimaryKey", got=owner_pk
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


    def change_slug(self, new_slug: Slug):
        self.validate_slug(new_slug)
        self._slug = new_slug

    def change_original_url(self, new_url: OriginalURL):
        self.validate_original_url(new_url)
        self._original_url = new_url

    def change_owner_pk(self, new_owner_pk: PrimaryKey):
        self.validate_owner_pk(new_owner_pk)
        self._owner_pk = new_owner_pk


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
            raise ShortURLAvailabilityError()

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
            f"<ShortURL pk={self.pk}, slug={self.slug}, original_url={self.original_url}>"
        )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shortener.domain.user import User
