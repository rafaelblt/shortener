from typing import Optional

from datetime import datetime

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.datetime_utils import is_utc

from .fields import Slug, TargetURL, ShortURLStatus, ShortURLID, OwnerID
from .exceptions import (
    ShortURLExpiredError,
    ShortURLDeactivatedError,
    ShortURLAttributeTypeError
)


class ShortURL(DomainEntity):

    @staticmethod
    def get_fields() -> list[str]:
        return [
            "id",
            "slug",
            "target_url",
            "owner_id",
            "status",
            "visit_count",
            "created_at",
            "expires_at",
            "last_accessed_at",
        ]

    def __init__(
        self,
        id: ShortURLID,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        created_at: datetime,
        status: ShortURLStatus = ShortURLStatus.ACTIVE,
        visit_count: int = 0,
        expires_at: Optional[datetime] = None,
        last_accessed_at: Optional[datetime] = None,
    ):
        self.validate_id(id)
        self.validate_slug(slug)
        self.validate_target_url(target_url)
        self.validate_owner_id(owner_id)
        self.validate_status(status)
        self.validate_visit_count(visit_count)
        self.validate_created_at(created_at)
        self.validate_expires_at(expires_at)
        self.validate_last_accessed_at(last_accessed_at)

        self._id = id
        self._slug = slug
        self._target_url = target_url
        self._owner_id = owner_id
        self._status = status
        self._visit_count = visit_count
        self._created_at = created_at
        self._expires_at = expires_at
        self._last_accessed_at = last_accessed_at

    @classmethod
    def create(
        cls,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        now: datetime,
        expires_at: Optional[datetime] = None,
    ) -> "ShortURL":
        return cls(
            id=ShortURLID.generate(),
            slug=slug,
            target_url=target_url,
            owner_id=owner_id,
            created_at=now,
            expires_at=expires_at,
        )


    @property
    def id(self):
        return self._id

    @property
    def slug(self):
        return self._slug

    @property
    def target_url(self):
        return self._target_url

    @property
    def owner_id(self):
        return self._owner_id

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


    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now

    def is_available(self, now: datetime) -> bool:
        return self.status == ShortURLStatus.ACTIVE and not self.is_expired(now)


    @staticmethod
    def validate_id(id):
        if not isinstance(id, ShortURLID):
            raise ShortURLAttributeTypeError(
                attr="id", type_expected="ShortURLID", got=id
            )

    @staticmethod
    def validate_slug(slug):
        if not isinstance(slug, Slug):
            raise ShortURLAttributeTypeError(
                attr="slug", type_expected="Slug", got=slug
            )

    @staticmethod
    def validate_target_url(target_url):
        if not isinstance(target_url, TargetURL):
            raise ShortURLAttributeTypeError(
                attr="target_url", type_expected="TargetURL", got=target_url
            )

    @staticmethod
    def validate_owner_id(owner_id):
        if not isinstance(owner_id, OwnerID):
            raise ShortURLAttributeTypeError(
                attr="owner_id", type_expected="OwnerID", got=owner_id
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

    def change_target_url(self, new_target_url: TargetURL):
        self.validate_target_url(new_target_url)
        self._target_url = new_target_url


    def record_visit(self, now: datetime):
        self.validate_last_accessed_at(now)
        self._visit_count = self.visit_count + 1
        self._last_accessed_at = now
    
    def resolve(self, now: datetime) -> TargetURL:
        """
        Returns the target_url if the ShortURL is available at the given moment.

        Raises:
            ShortURLDeactivatedError: If the ShortURL status is DEACTIVATED.
            ShortURLExpiredError: If the ShortURL status is ACTIVE and
                expires_at has been reached.
        """
        if self.status == ShortURLStatus.DEACTIVATED:
            raise ShortURLDeactivatedError()
        if self.is_expired(now):
            raise ShortURLExpiredError()
        return self.target_url

    def enable(self):
        self._status = ShortURLStatus.ACTIVE

    def disable(self):
        self._status = ShortURLStatus.DEACTIVATED

    def __repr__(self):
        return (
            f"<ShortURL id={self.id}, slug={self.slug}, target_url={self.target_url}>"
        )
