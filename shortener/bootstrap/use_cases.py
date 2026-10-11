from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final, cast

from shortener.use_cases.clock import Clock
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.disable_shorturl import DisableShortURL
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.list_shorturls import ListShortURLs
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.shorturl_repository import ShortURLReader
from shortener.use_cases.unit_of_work import UnitOfWork
from shortener.use_cases.update_shorturl import UpdateShortURL


@dataclass(frozen=True)
class UseCases:
    """
    The UseCaseFactory of the API, which builds each use case with the
    implementations of its abstractions. See docs/bootstrap.md#use-cases
    """

    uow: UnitOfWork
    shorturls: ShortURLReader
    clock: Clock

    def build[T](self, use_case: type[T], current_user: CurrentUser) -> T:
        """
        Raises:
            LookupError: The use case isn't one UseCases builds.
        """
        try:
            builder = _BUILDERS[use_case]
        except KeyError:
            raise LookupError(
                f"UseCases doesn't build {use_case.__name__}. Add it to _BUILDERS, "
                "in shortener/bootstrap/use_cases.py"
            ) from None
        return cast(T, builder(self, current_user))


_BUILDERS: Final[dict[type, Callable[[UseCases, CurrentUser], Any]]] = {
    ResolveSlug: lambda use_cases, current_user: ResolveSlug(
        use_cases.uow, use_cases.clock
    ),
    CreateShortURL: lambda use_cases, current_user: CreateShortURL(
        use_cases.uow, current_user, use_cases.clock
    ),
    GetShortURL: lambda use_cases, current_user: GetShortURL(
        use_cases.shorturls, current_user
    ),
    ListShortURLs: lambda use_cases, current_user: ListShortURLs(
        use_cases.shorturls, current_user
    ),
    UpdateShortURL: lambda use_cases, current_user: UpdateShortURL(
        use_cases.uow, current_user
    ),
    EnableShortURL: lambda use_cases, current_user: EnableShortURL(
        use_cases.uow, current_user
    ),
    DisableShortURL: lambda use_cases, current_user: DisableShortURL(
        use_cases.uow, current_user
    ),
    DeleteShortURL: lambda use_cases, current_user: DeleteShortURL(
        use_cases.uow, current_user
    ),
}
