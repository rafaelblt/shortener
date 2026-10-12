import httpx
import pytest

from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any
from uuid import UUID

from pydantic import TypeAdapter

from shortener.api.cursors import decode_cursor, encode_cursor
from shortener.domain import ShortURL
from shortener.domain.errors import ShortURLDeactivatedError
from shortener.shared.result import Err, Ok
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.disable_shorturl import DisableShortURL
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.errors import ShortURLNotFoundError
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.list_shorturls import DEFAULT_PAGE_SIZE, ListShortURLs
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.resolved_slug import ResolvedSlug
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_page import ShortURLPage
from shortener.use_cases.update_shorturl import UpdateShortURL
from tests.fixtures.api.doubles import AUTHORIZATION, UseCaseDoubles


ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20")
CURSOR = ShortURLCursor(created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), id=ID)


@pytest.fixture
def details(normal_shorturl: ShortURL) -> ShortURLDetails:
    return ShortURLDetails.from_entity(normal_shorturl)


def as_json(value: object) -> Any:
    return TypeAdapter(type(value)).dump_python(value, mode="json")


@pytest.mark.parametrize(
    "method, url, body, use_case, arguments",
    [
        pytest.param(
            "GET",
            "/v1/slugs/my-slug",
            None,
            ResolveSlug,
            {"slug": "my-slug"},
            id="resolve",
        ),
        pytest.param(
            "GET",
            "/v1/slugs/my-slug/redirect",
            None,
            ResolveSlug,
            {"slug": "my-slug"},
            id="resolve and redirect",
        ),
        pytest.param(
            "POST",
            "/v1/shorturls",
            {"target_url": "https://example.com"},
            CreateShortURL,
            {"target_url": "https://example.com", "slug": None},
            id="create",
        ),
        pytest.param(
            "POST",
            "/v1/shorturls",
            {"target_url": "https://example.com", "slug": "my-slug"},
            CreateShortURL,
            {"target_url": "https://example.com", "slug": "my-slug"},
            id="create with a slug",
        ),
        pytest.param(
            "GET",
            "/v1/shorturls",
            None,
            ListShortURLs,
            {"limit": DEFAULT_PAGE_SIZE, "cursor": None},
            id="list",
        ),
        pytest.param(
            "GET",
            f"/v1/shorturls?limit=5&cursor={encode_cursor(CURSOR)}",
            None,
            ListShortURLs,
            {"limit": 5, "cursor": CURSOR},
            id="list after a cursor",
        ),
        pytest.param(
            "GET", f"/v1/shorturls/{ID}", None, GetShortURL, {"id": ID}, id="get"
        ),
        pytest.param(
            "PATCH",
            f"/v1/shorturls/{ID}",
            {"slug": "my-slug"},
            UpdateShortURL,
            {"id": ID, "target_url": None, "slug": "my-slug"},
            id="update",
        ),
        pytest.param(
            "POST",
            f"/v1/shorturls/{ID}/enable",
            None,
            EnableShortURL,
            {"id": ID},
            id="enable",
        ),
        pytest.param(
            "POST",
            f"/v1/shorturls/{ID}/disable",
            None,
            DisableShortURL,
            {"id": ID},
            id="disable",
        ),
        pytest.param(
            "DELETE",
            f"/v1/shorturls/{ID}",
            None,
            DeleteShortURL,
            {"id": ID},
            id="delete",
        ),
    ],
)
async def test_runs_its_use_case_with_the_values_of_the_request(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    method: str,
    url: str,
    body: dict[str, str] | None,
    use_case: type,
    arguments: dict[str, object],
):
    double = use_cases.double(use_case)
    double.execute.return_value = Err(ShortURLNotFoundError())

    await client.request(method, url, json=body, headers=AUTHORIZATION)

    double.execute.assert_awaited_once_with(**arguments)


async def test_post_shorturls_answers_created_with_the_details_of_the_new_shorturl(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles, details: ShortURLDetails
):
    use_cases.double(CreateShortURL).execute.return_value = Ok(details)

    response = await client.post(
        "/v1/shorturls", json={"target_url": details.target_url}, headers=AUTHORIZATION
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == as_json(details)


@pytest.mark.parametrize(
    "method, url, body, use_case",
    [
        pytest.param("GET", f"/v1/shorturls/{ID}", None, GetShortURL, id="get"),
        pytest.param(
            "PATCH", f"/v1/shorturls/{ID}", {"slug": "new"}, UpdateShortURL, id="update"
        ),
        pytest.param(
            "POST", f"/v1/shorturls/{ID}/enable", None, EnableShortURL, id="enable"
        ),
        pytest.param(
            "POST", f"/v1/shorturls/{ID}/disable", None, DisableShortURL, id="disable"
        ),
    ],
)
async def test_answers_the_details_of_the_shorturl_its_use_case_returns(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    details: ShortURLDetails,
    method: str,
    url: str,
    body: dict[str, str] | None,
    use_case: type,
):
    use_cases.double(use_case).execute.return_value = Ok(details)

    response = await client.request(method, url, json=body, headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == as_json(details)


async def test_get_shorturls_answers_the_page_with_a_cursor_that_a_request_takes_back(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles, details: ShortURLDetails
):
    use_cases.double(ListShortURLs).execute.return_value = Ok(
        ShortURLPage(items=(details,), next_cursor=CURSOR)
    )

    response = await client.get("/v1/shorturls", headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["items"] == [as_json(details)]
    assert decode_cursor(content["next_cursor"]) == CURSOR


async def test_get_shorturls_answers_no_cursor_after_the_last_page(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(ListShortURLs).execute.return_value = Ok(
        ShortURLPage(items=(), next_cursor=None)
    )

    response = await client.get("/v1/shorturls", headers=AUTHORIZATION)

    assert response.json() == {"items": [], "next_cursor": None}


async def test_get_slug_answers_its_target_url(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(ResolveSlug).execute.return_value = Ok(
        ResolvedSlug(target_url="https://example.com/page")
    )

    response = await client.get("/v1/slugs/my-slug")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"target_url": "https://example.com/page"}


async def test_get_slug_redirect_redirects_to_its_target_url(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(ResolveSlug).execute.return_value = Ok(
        ResolvedSlug(target_url="https://example.com/page")
    )

    response = await client.get("/v1/slugs/my-slug/redirect")

    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert response.headers["Location"] == "https://example.com/page"


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("/v1/slugs/my-slug", id="resolve"),
        pytest.param("/v1/slugs/my-slug/redirect", id="resolve and redirect"),
    ],
)
async def test_the_endpoints_of_a_slug_tell_a_deactivated_shorturl_apart(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles, url: str
):
    use_cases.double(ResolveSlug).execute.return_value = Err(
        ShortURLDeactivatedError()
    )

    response = await client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["code"] == "shorturl_deactivated"


async def test_delete_shorturl_answers_no_content(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(DeleteShortURL).execute.return_value = Ok(None)

    response = await client.delete(f"/v1/shorturls/{ID}", headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""
