from typing import Optional

from datetime import datetime

from .slug import Slug
from .target_url import TargetURL
from .status import ShortURLStatus
from .shorturl_id import ShortURLID
from .owner_id import OwnerID
from .exceptions import ShortURLDeactivatedError


class ShortURL:

    def __init__(
        self,
        id: ShortURLID,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        status: ShortURLStatus,
        resolution_count: int,
        created_at: datetime,
        last_resolved_at: Optional[datetime],
    ):
        _check_attribute_type("id", id, ShortURLID)
        _check_attribute_type("slug", slug, Slug)
        _check_attribute_type("target_url", target_url, TargetURL)
        _check_attribute_type("owner_id", owner_id, OwnerID)
        _check_attribute_type("status", status, ShortURLStatus)
        _check_resolution_count(resolution_count)
        _check_attribute_type("created_at", created_at, datetime)
        if last_resolved_at is not None:
            _check_attribute_type("last_resolved_at", last_resolved_at, datetime)

        self._id = id
        self._slug = slug
        self._target_url = target_url
        self._owner_id = owner_id
        self._status = status
        self._resolution_count = resolution_count
        self._created_at = created_at
        self._last_resolved_at = last_resolved_at

    @classmethod
    def create(
        cls,
        slug: Slug,
        target_url: TargetURL,
        owner_id: OwnerID,
        now: datetime,
    ) -> "ShortURL":
        return cls(
            id=ShortURLID.generate(),
            slug=slug,
            target_url=target_url,
            owner_id=owner_id,
            status=ShortURLStatus.ACTIVE,
            resolution_count=0,
            created_at=now,
            last_resolved_at=None,
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
        resolution_count: int,
        created_at: datetime,
        last_resolved_at: Optional[datetime],
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
            resolution_count=resolution_count,
            created_at=created_at,
            last_resolved_at=last_resolved_at,
        )


    @property
    def id(self) -> ShortURLID:
        return self._id

    @property
    def slug(self) -> Slug:
        return self._slug

    @property
    def target_url(self) -> TargetURL:
        return self._target_url

    @property
    def owner_id(self) -> OwnerID:
        return self._owner_id

    @property
    def status(self) -> ShortURLStatus:
        return self._status

    @property
    def resolution_count(self) -> int:
        return self._resolution_count

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def last_resolved_at(self) -> Optional[datetime]:
        return self._last_resolved_at


    def change_slug(self, new_slug: Slug):
        _check_attribute_type("slug", new_slug, Slug)
        self._slug = new_slug

    def change_target_url(self, new_target_url: TargetURL):
        _check_attribute_type("target_url", new_target_url, TargetURL)
        self._target_url = new_target_url


    def resolve(self, now: datetime) -> TargetURL:
        """
        Counts the resolution and returns the target_url if the ShortURL is
        available.

        Raises:
            TypeError: If now isn't a datetime.
            ShortURLDeactivatedError: If the ShortURL status is DEACTIVATED.
        """
        _check_parameter_type("now", now, datetime)
        if self.status == ShortURLStatus.DEACTIVATED:
            raise ShortURLDeactivatedError()
        self._resolution_count = self.resolution_count + 1
        self._last_resolved_at = now
        return self.target_url

    def enable(self):
        self._status = ShortURLStatus.ACTIVE

    def disable(self):
        self._status = ShortURLStatus.DEACTIVATED

    def __repr__(self):
        return (
            f"<ShortURL id={self.id}, slug={self.slug}, target_url={self.target_url}>"
        )


def _check_attribute_type(attribute: str, value: object, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(
            f"The ShortURL {attribute} must be an instance of "
            f"{expected_type.__name__}, got {type(value).__name__}"
        )


def _check_parameter_type(parameter: str, value: object, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(
            f"The {parameter} parameter must be an instance of "
            f"{expected_type.__name__}, got {type(value).__name__}"
        )


def _check_resolution_count(resolution_count: int) -> None:
    _check_attribute_type("resolution_count", resolution_count, int)
    if resolution_count < 0:
        raise ValueError(
            "The ShortURL resolution_count must be greater than or equal to 0, "
            f"got {resolution_count}"
        )
