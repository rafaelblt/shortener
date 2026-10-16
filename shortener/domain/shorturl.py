from datetime import datetime

from shortener.domain.errors import ShortURLDeactivatedError
from shortener.domain.shorturl_id import ShortURLID
from shortener.domain.slug import Slug
from shortener.domain.status import ShortURLStatus
from shortener.domain.target_url import TargetURL
from shortener.domain.user_id import UserID
from shortener.shared.result import Err, Ok, Result
from shortener.shared.type_checks import check_parameter_type


class ShortURL:
    def __init__(
        self,
        id: ShortURLID,
        slug: Slug,
        target_url: TargetURL,
        owner_id: UserID,
        status: ShortURLStatus,
        resolution_count: int,
        created_at: datetime,
        last_resolved_at: datetime | None,
    ):
        _check_attribute_type("id", id, ShortURLID)
        _check_attribute_type("slug", slug, Slug)
        _check_attribute_type("target_url", target_url, TargetURL)
        _check_attribute_type("owner_id", owner_id, UserID)
        _check_attribute_type("status", status, ShortURLStatus)
        _check_resolution_count(resolution_count)
        _check_attribute_type("created_at", created_at, datetime)
        _check_timezone_aware("created_at", created_at)
        if last_resolved_at is not None:
            _check_attribute_type("last_resolved_at", last_resolved_at, datetime)
            _check_timezone_aware("last_resolved_at", last_resolved_at)

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
        owner_id: UserID,
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
        owner_id: UserID,
        status: ShortURLStatus,
        resolution_count: int,
        created_at: datetime,
        last_resolved_at: datetime | None,
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
    def owner_id(self) -> UserID:
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
    def last_resolved_at(self) -> datetime | None:
        return self._last_resolved_at

    def change_slug(self, new_slug: Slug):
        _check_attribute_type("slug", new_slug, Slug)
        self._slug = new_slug

    def change_target_url(self, new_target_url: TargetURL):
        _check_attribute_type("target_url", new_target_url, TargetURL)
        self._target_url = new_target_url

    def resolve(self, now: datetime) -> Result[TargetURL, ShortURLDeactivatedError]:
        """
        Counts the resolution and returns Ok with the target_url if the ShortURL
        is available. Otherwise, returns Err and counts nothing.

        Raises:
            TypeError: If now isn't a datetime.
            ValueError: If now is naive.
        """
        check_parameter_type("now", now, datetime)
        _check_timezone_aware("now", now)
        if self.status == ShortURLStatus.DEACTIVATED:
            return Err(ShortURLDeactivatedError())
        self._resolution_count = self.resolution_count + 1
        self._last_resolved_at = now
        return Ok(self.target_url)

    def enable(self):
        self._status = ShortURLStatus.ACTIVE

    def disable(self):
        self._status = ShortURLStatus.DEACTIVATED

    def __repr__(self):
        return (
            f"<ShortURL id={self.id}, slug={self.slug}, target_url={self.target_url}>"
        )


# Only ShortURL checks its attributes, so the check stays here, with the class
# name written in the message. If another entity needs it, consider moving it
# to shortener/shared/, taking the class name from the entity itself.
def _check_attribute_type(attribute: str, value: object, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(
            f"The ShortURL {attribute} must be an instance of "
            f"{expected_type.__name__}, got {type(value).__name__}"
        )


# A datetime is naive when utcoffset() returns None, as Python defines it.
def _check_timezone_aware(name: str, value: datetime) -> None:
    if value.utcoffset() is None:
        raise ValueError(f"The {name} datetime must be timezone-aware, got {value}")


def _check_resolution_count(resolution_count: int) -> None:
    _check_attribute_type("resolution_count", resolution_count, int)
    if resolution_count < 0:
        raise ValueError(
            "The ShortURL resolution_count must be greater than or equal to 0, "
            f"got {resolution_count}"
        )
