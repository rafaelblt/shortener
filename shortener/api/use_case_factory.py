from typing import Protocol

from shortener.use_cases.current_user import CurrentUser


class UseCaseFactory(Protocol):
    def build[T](self, use_case: type[T], current_user: CurrentUser) -> T:
        """
        Returns the use case for one request, which is made by current_user.
        See docs/api.md#use-cases
        """
        ...
