import httpx
import pytest

from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from unittest.mock import NonCallableMagicMock
from uuid import UUID

from fastapi import FastAPI

from shortener.api.app import create_app
from shortener.api.cursors import encode_cursor
from shortener.api.endpoint import Endpoint
from shortener.api.responses import Created
from shortener.domain import UserID
from shortener.shared.result import Err, Ok, Result
from shortener.use_cases.clock import Clock
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.errors import ShortURLNotFoundError
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from tests.fixtures.api.doubles import ACCESS_TOKEN, AUTHORIZATION, UseCaseDoubles
from tests.utils.text_helpers import assert_mentions


ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20")
CURSOR = ShortURLCursor(created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), id=ID)
SUMMARY = "Echo the values of the request"
TAG = "Echoes"


@dataclass(frozen=True)
class Echoed:
    name: str


@dataclass(frozen=True)
class UnansweredError:
    """An error the API doesn't answer."""


class Echo:
    """A use case whose execute() has parameters of every kind."""

    def __init__(self, current_user: CurrentUser): ...

    async def execute(
        self,
        id: UUID,
        name: str,
        count: int = 1,
        cursor: ShortURLCursor | None = None,
    ) -> Result[Echoed, ShortURLNotFoundError]: ...


class Public:
    """A use case that doesn't take a CurrentUser."""

    def __init__(self, clock: Clock): ...

    async def execute(self) -> Result[Echoed, ShortURLNotFoundError]: ...


class Unanswered:
    def __init__(self, current_user: CurrentUser): ...

    async def execute(self) -> Result[Echoed, UnansweredError]: ...


@pytest.fixture
def app(
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    rate_limiter: NonCallableMagicMock,
    health_check: NonCallableMagicMock,
) -> FastAPI:
    return create_app(
        use_cases=use_cases,
        access_token_verifier=access_token_verifier,
        rate_limiter=rate_limiter,
        health_check=health_check,
        endpoints=[
            Endpoint("PUT", "/echoes/{id}", Echo, summary=SUMMARY, tag=TAG),
            Endpoint(
                "POST",
                "/echoes",
                Echo,
                Created(lambda echoed: f"/v1/echoes/{echoed.name}"),
                summary="Create an echo",
                tag=TAG,
                name="CreateEcho",
            ),
            Endpoint(
                "GET",
                "/echoes/{id}",
                Echo,
                summary="Echo the values of the query",
                tag=TAG,
                name="EchoFromTheQuery",
            ),
            Endpoint(
                "GET", "/public", Public, summary="Run a public use case", tag=TAG
            ),
        ],
    )


@pytest.fixture
def echo(use_cases: UseCaseDoubles) -> NonCallableMagicMock:
    echo = use_cases.double(Echo)
    echo.execute.return_value = Ok(Echoed(name="echoed"))
    return echo


@pytest.fixture
def public(use_cases: UseCaseDoubles) -> NonCallableMagicMock:
    public = use_cases.double(Public)
    public.execute.return_value = Ok(Echoed(name="public"))
    return public


async def test_receives_the_parameters_of_the_path_from_it_and_the_others_from_the_body(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    await client.put(
        f"/v1/echoes/{ID}",
        json={"name": "my-name", "count": 2, "cursor": encode_cursor(CURSOR)},
        headers=AUTHORIZATION,
    )

    echo.execute.assert_awaited_once_with(id=ID, name="my-name", count=2, cursor=CURSOR)


async def test_receives_the_parameters_out_of_the_path_from_the_query_for_a_get(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    await client.get(
        f"/v1/echoes/{ID}",
        params={"name": "my-name", "count": "2", "cursor": encode_cursor(CURSOR)},
        headers=AUTHORIZATION,
    )

    echo.execute.assert_awaited_once_with(id=ID, name="my-name", count=2, cursor=CURSOR)


async def test_gives_the_defaults_of_execute_for_the_values_the_request_lacks(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    await client.put(
        f"/v1/echoes/{ID}", json={"name": "my-name"}, headers=AUTHORIZATION
    )

    echo.execute.assert_awaited_once_with(id=ID, name="my-name", count=1, cursor=None)


async def test_answers_missing_for_a_value_without_a_default_that_the_request_lacks(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    response = await client.put(f"/v1/echoes/{ID}", json={}, headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["fields"] == [
        {"field": "name", "issues": [{"code": "missing"}]}
    ]
    echo.execute.assert_not_awaited()


async def test_answers_the_value_of_ok_as_json(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    response = await client.put(
        f"/v1/echoes/{ID}", json={"name": "my-name"}, headers=AUTHORIZATION
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"name": "echoed"}


async def test_answers_the_error_its_use_case_returns(
    client: httpx.AsyncClient, echo: NonCallableMagicMock
):
    echo.execute.return_value = Err(ShortURLNotFoundError())

    response = await client.put(
        f"/v1/echoes/{ID}", json={"name": "my-name"}, headers=AUTHORIZATION
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["code"] == "shorturl_not_found"


async def test_builds_the_use_case_with_the_user_of_the_access_token(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    echo: NonCallableMagicMock,
    owner_id: UserID,
):
    await client.put(
        f"/v1/echoes/{ID}", json={"name": "my-name"}, headers=AUTHORIZATION
    )

    assert await use_cases.current_users[0].get_id() == owner_id
    access_token_verifier.verify.assert_awaited_once_with(ACCESS_TOKEN)


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({}, id="no authorization"),
        pytest.param({"Authorization": "Basic dXNlcjpwYXNz"}, id="another scheme"),
    ],
)
async def test_builds_the_use_case_with_no_user_when_the_request_has_no_access_token(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    echo: NonCallableMagicMock,
    headers: dict[str, str],
):
    await client.put(f"/v1/echoes/{ID}", json={"name": "my-name"}, headers=headers)

    assert await use_cases.current_users[0].get_id() is None
    access_token_verifier.verify.assert_not_awaited()


async def test_ignores_the_access_token_when_the_use_case_takes_no_current_user(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    public: NonCallableMagicMock,
):
    await client.get("/v1/public", headers=AUTHORIZATION)

    assert await use_cases.current_users[0].get_id() is None
    access_token_verifier.verify.assert_not_awaited()


def test_names_the_endpoint_after_its_use_case_unless_it_has_a_name(app: FastAPI):
    paths = app.openapi()["paths"]

    assert paths["/v1/echoes/{id}"]["put"]["operationId"] == Echo.__name__
    assert paths["/v1/echoes/{id}"]["get"]["operationId"] == "EchoFromTheQuery"


def test_documents_the_summary_of_the_endpoint(app: FastAPI):
    operation = app.openapi()["paths"]["/v1/echoes/{id}"]["put"]

    assert operation["summary"] == SUMMARY


def test_documents_the_tag_of_the_endpoint(app: FastAPI):
    operation = app.openapi()["paths"]["/v1/echoes/{id}"]["put"]

    assert operation["tags"] == [TAG]


def test_documents_the_access_token_only_where_the_use_case_takes_a_current_user(
    app: FastAPI,
):
    paths = app.openapi()["paths"]

    assert "security" in paths["/v1/echoes/{id}"]["put"]
    assert "security" not in paths["/v1/public"]["get"]


def test_documents_the_ok_of_the_use_case_and_its_errors_by_status(app: FastAPI):
    schema = app.openapi()
    responses = schema["paths"]["/v1/echoes/{id}"]["put"]["responses"]

    ok_schema = responses[str(HTTPStatus.OK.value)]["content"]["application/json"]
    assert ok_schema["schema"]["$ref"].endswith("/Echoed")
    assert_mentions(
        responses[str(HTTPStatus.NOT_FOUND.value)]["description"], "shorturl_not_found"
    )
    for status in [
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ]:
        assert str(status.value) in responses


def test_describes_the_response_of_ok_by_its_status(app: FastAPI):
    responses = app.openapi()["paths"]["/v1/echoes/{id}"]["put"]["responses"]

    assert responses[str(HTTPStatus.OK.value)]["description"] == HTTPStatus.OK.phrase


def test_documents_the_headers_of_its_response_of_ok(app: FastAPI):
    responses = app.openapi()["paths"]["/v1/echoes"]["post"]["responses"]

    headers = responses[str(HTTPStatus.CREATED.value)]["headers"]
    assert set(headers) == set(Created.header_descriptions)


def test_documents_no_body_errors_for_an_endpoint_without_a_body(app: FastAPI):
    responses = app.openapi()["paths"]["/v1/public"]["get"]["responses"]

    assert str(HTTPStatus.BAD_REQUEST.value) not in responses
    assert str(HTTPStatus.UNPROCESSABLE_ENTITY.value) not in responses


def test_creating_the_app_raises_for_an_error_of_a_use_case_the_api_does_not_answer(
    use_cases: UseCaseDoubles,
    access_token_verifier: NonCallableMagicMock,
    rate_limiter: NonCallableMagicMock,
    health_check: NonCallableMagicMock,
):
    with pytest.raises(LookupError) as raised:
        create_app(
            use_cases=use_cases,
            access_token_verifier=access_token_verifier,
            rate_limiter=rate_limiter,
            health_check=health_check,
            endpoints=[
                Endpoint(
                    "GET",
                    "/unanswered",
                    Unanswered,
                    summary="Answer nothing",
                    tag=TAG,
                )
            ],
        )
    assert_mentions(str(raised.value), UnansweredError.__name__)
