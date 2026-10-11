import pytest

from typing import Any
from unittest.mock import NonCallableMagicMock
from uuid import UUID

from shortener.api.endpoints import ENDPOINTS
from shortener.bootstrap.use_cases import UseCases
from shortener.domain import ShortURL
from shortener.shared.result import Err
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.disable_shorturl import DisableShortURL
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.errors import NotAuthenticatedError
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.list_shorturls import ListShortURLs
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.update_shorturl import UpdateShortURL
from tests.utils.text_helpers import assert_mentions


ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20")

# Use cases, with the arguments of a call to execute().
WITH_A_CURRENT_USER = [
    pytest.param(CreateShortURL, {"target_url": "https://example.com"}, id="create"),
    pytest.param(GetShortURL, {"id": ID}, id="get"),
    pytest.param(ListShortURLs, {}, id="list"),
    pytest.param(UpdateShortURL, {"id": ID, "slug": "my-slug"}, id="update"),
    pytest.param(EnableShortURL, {"id": ID}, id="enable"),
    pytest.param(DisableShortURL, {"id": ID}, id="disable"),
    pytest.param(DeleteShortURL, {"id": ID}, id="delete"),
]
WITH_THE_UNIT_OF_WORK = [
    pytest.param(ResolveSlug, {"slug": "my-slug"}, id="resolve"),
    pytest.param(CreateShortURL, {"target_url": "https://example.com"}, id="create"),
    pytest.param(UpdateShortURL, {"id": ID, "slug": "my-slug"}, id="update"),
    pytest.param(EnableShortURL, {"id": ID}, id="enable"),
    pytest.param(DisableShortURL, {"id": ID}, id="disable"),
    pytest.param(DeleteShortURL, {"id": ID}, id="delete"),
]


@pytest.fixture
def use_cases(
    uow: NonCallableMagicMock,
    shorturl_reader: NonCallableMagicMock,
    clock: NonCallableMagicMock,
) -> UseCases:
    return UseCases(uow=uow, shorturls=shorturl_reader, clock=clock)


@pytest.mark.parametrize(
    "use_case",
    [
        pytest.param(endpoint.use_case, id=endpoint.use_case.__name__)
        for endpoint in ENDPOINTS
    ],
)
def test_build_builds_the_use_case_of_each_endpoint(
    use_cases: UseCases, current_user: NonCallableMagicMock, use_case: type
):
    assert isinstance(use_cases.build(use_case, current_user), use_case)


def test_build_raises_for_a_use_case_it_does_not_build(
    use_cases: UseCases, current_user: NonCallableMagicMock
):
    class Unknown: ...

    with pytest.raises(LookupError) as raised:
        use_cases.build(Unknown, current_user)
    assert_mentions(str(raised.value), Unknown.__name__)


@pytest.mark.parametrize("use_case, arguments", WITH_A_CURRENT_USER)
async def test_build_gives_the_current_user_to_the_use_cases_that_take_one(
    use_cases: UseCases,
    current_user: NonCallableMagicMock,
    use_case: type,
    arguments: dict[str, Any],
):
    current_user.get_id.return_value = None

    result = await use_cases.build(use_case, current_user).execute(**arguments)

    assert result == Err(NotAuthenticatedError())
    current_user.get_id.assert_awaited_once()


@pytest.mark.parametrize("use_case, arguments", WITH_THE_UNIT_OF_WORK)
async def test_build_gives_the_unit_of_work_to_the_use_cases_that_write(
    use_cases: UseCases,
    current_user: NonCallableMagicMock,
    uow: NonCallableMagicMock,
    use_case: type,
    arguments: dict[str, Any],
):
    await use_cases.build(use_case, current_user).execute(**arguments)
    uow.begin.assert_called_once()


@pytest.mark.parametrize(
    "use_case, arguments, read",
    [
        pytest.param(GetShortURL, {"id": ID}, "get_by_id", id="get"),
        pytest.param(ListShortURLs, {}, "list_by_owner", id="list"),
    ],
)
async def test_build_gives_the_reader_to_the_use_cases_that_only_read(
    use_cases: UseCases,
    current_user: NonCallableMagicMock,
    shorturl_reader: NonCallableMagicMock,
    use_case: type,
    arguments: dict[str, Any],
    read: str,
):
    await use_cases.build(use_case, current_user).execute(**arguments)
    getattr(shorturl_reader, read).assert_awaited_once()


async def test_build_gives_the_clock_to_the_use_cases_that_take_one(
    use_cases: UseCases,
    current_user: NonCallableMagicMock,
    clock: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    normal_shorturl: ShortURL,
):
    transaction.shorturls.get_by_slug.return_value = normal_shorturl

    await use_cases.build(ResolveSlug, current_user).execute(normal_shorturl.slug)
    await use_cases.build(CreateShortURL, current_user).execute("https://example.com")

    assert clock.now.call_count == 2
