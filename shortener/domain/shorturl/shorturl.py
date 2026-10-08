from typing import Optional

from datetime import datetime

from .slug import Slug
from .target_url import TargetURL
from .status import ShortURLStatus
from .shorturl_id import ShortURLID
from .owner_id import OwnerID
from .exceptions import (
    ShortURLExpiredError,
    ShortURLDeactivatedError,
    ShortURLAttributeTypeError
)


class ShortURL:

    def __init__(
        self,
        id: ShortURLID,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        status: ShortURLStatus,
        visit_count: int,
        created_at: datetime,
        expires_at: Optional[datetime],
        last_accessed_at: Optional[datetime],
    ):
        _check_type("id", id, ShortURLID)
        _check_type("slug", slug, Slug)
        _check_type("target_url", target_url, TargetURL)
        _check_type("owner_id", owner_id, OwnerID)
        _check_type("status", status, ShortURLStatus)
        _check_visit_count(visit_count)
        _check_type("created_at", created_at, datetime)
        _check_optional_datetime("expires_at", expires_at)
        _check_optional_datetime("last_accessed_at", last_accessed_at)

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
            status=ShortURLStatus.ACTIVE,
            visit_count=0,
            created_at=now,
            expires_at=expires_at,
            last_accessed_at=None,
        )

    @classmethod
    def restore(
        cls,
        *,
        id: ShortURLID,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        status: ShortURLStatus,
        visit_count: int,
        created_at: datetime,
        expires_at: Optional[datetime],
        last_accessed_at: Optional[datetime],
    ) -> "ShortURL":
        """
        Rebuilds a short URL that already exists, such as one loaded from the
        database. It repeats the parameters of the constructor on purpose. See
        docs/domain.md#creating-and-restoring
        """
        return cls(
            id=id,
            slug=slug,
            target_url=target_url,
            owner_id=owner_id,
            status=status,
            visit_count=visit_count,
            created_at=created_at,
            expires_at=expires_at,
            last_accessed_at=last_accessed_at,
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


    def change_slug(self, new_slug: Slug):
        _check_type("slug", new_slug, Slug)
        self._slug = new_slug

    def change_target_url(self, new_target_url: TargetURL):
        _check_type("target_url", new_target_url, TargetURL)
        self._target_url = new_target_url


    def record_visit(self, now: datetime):
        _check_type("last_accessed_at", now, datetime)
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


def _check_type(attribute: str, value: object, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        raise ShortURLAttributeTypeError(
            attr=attribute, type_expected=expected_type.__name__, got=value
        )


def _check_visit_count(visit_count: int) -> None:
    _check_type("visit_count", visit_count, int)
    if visit_count < 0:
        raise ValueError(
            "The ShortURL visit_count must be greater than or equal to 0, "
            f"got {visit_count}"
        )


def _check_optional_datetime(attribute: str, value: Optional[datetime]) -> None:
    if value is not None and not isinstance(value, datetime):
        raise ShortURLAttributeTypeError(
            attr=attribute, type_expected="datetime or None", got=value
        )
