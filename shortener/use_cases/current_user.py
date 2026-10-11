from typing import Protocol

from shortener.domain import UserID


class CurrentUser(Protocol):
    """The user making the request. See docs/use_cases.md#current-user"""

    async def get_id(self) -> UserID | None:
        """
        Returns None when there is no authenticated user. Whether that is an
        error is up to the use case.
        """
        ...
