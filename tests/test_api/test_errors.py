import httpx
import json
import logging
import pytest

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from shortener.api.errors import error_response
from shortener.domain import Slug
from shortener.domain.errors import ShortURLDeactivatedError
from shortener.shared.validation import IssueCode
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.errors import (
    FieldError,
    InvalidInputError,
    NotAuthenticatedError,
    NothingToUpdateError,
    ShortURLNotFoundError,
)
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.shorturl_repository import SlugTakenError
from shortener.use_cases.unavailable_error import UnavailableError
from tests.fixtures.api.doubles import AUTHORIZATION, UseCaseDoubles
from tests.fixtures.shared.validation import invalid
from tests.utils.text_helpers import assert_mentions


ID = "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20"


def content_of(response: Any) -> Any:
    return json.loads(response.body)


@pytest.mark.parametrize(
    "error, status, code",
    [
        pytest.param(
            NotAuthenticatedError(),
            HTTPStatus.UNAUTHORIZED,
            "not_authenticated",
            id="not authenticated",
        ),
        pytest.param(
            InvalidInputError(()),
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "invalid_input",
            id="invalid input",
        ),
        pytest.param(
            NothingToUpdateError(),
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "nothing_to_update",
            id="nothing to update",
        ),
        pytest.param(
            ShortURLNotFoundError(),
            HTTPStatus.NOT_FOUND,
            "shorturl_not_found",
            id="shorturl not found",
        ),
        pytest.param(
            ShortURLDeactivatedError(),
            HTTPStatus.NOT_FOUND,
            "shorturl_deactivated",
            id="shorturl deactivated",
        ),
        pytest.param(
            SlugTakenError(Slug("my-slug")),
            HTTPStatus.CONFLICT,
            "slug_taken",
            id="slug taken",
        ),
    ],
)
def test_error_response_answers_each_error_with_its_status_and_code(
    error: object, status: HTTPStatus, code: str
):
    response = error_response(error)

    assert response.status_code == status
    assert content_of(response)["code"] == code


def test_error_response_names_each_invalid_value_with_the_codes_of_its_issues():
    error = InvalidInputError(
        (
            FieldError("target_url", invalid(IssueCode.INVALID_FORMAT).error),
            FieldError(
                "slug", invalid(IssueCode.INVALID_FORMAT, IssueCode.TOO_SHORT).error
            ),
        )
    )

    content = content_of(error_response(error))

    assert content["fields"] == [
        {"field": "target_url", "issues": [{"code": "invalid_format"}]},
        {
            "field": "slug",
            "issues": [{"code": "invalid_format"}, {"code": "too_short"}],
        },
    ]


def test_error_response_has_no_fields_for_errors_of_other_kinds():
    assert "fields" not in content_of(error_response(ShortURLNotFoundError()))


def test_error_response_asks_for_a_bearer_token_when_the_user_is_not_authenticated():
    response = error_response(NotAuthenticatedError())
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_error_response_raises_for_an_error_the_api_does_not_answer():
    @dataclass(frozen=True)
    class UnansweredError: ...

    with pytest.raises(LookupError) as raised:
        error_response(UnansweredError())
    assert_mentions(str(raised.value), UnansweredError.__name__)


@pytest.mark.parametrize(
    "method, url, body, field, code",
    [
        pytest.param(
            "GET", "/v1/shorturls/not-a-uuid", None, "id", "invalid_type", id="id"
        ),
        pytest.param(
            "GET", "/v1/shorturls?limit=ten", None, "limit", "invalid_type", id="limit"
        ),
        pytest.param(
            "GET",
            "/v1/shorturls?cursor=not-a-cursor",
            None,
            "cursor",
            "invalid_format",
            id="cursor",
        ),
        pytest.param(
            "POST", "/v1/shorturls", {}, "target_url", "missing", id="missing value"
        ),
        pytest.param(
            "POST",
            "/v1/shorturls",
            {"target_url": 10},
            "target_url",
            "invalid_type",
            id="value of another type",
        ),
    ],
)
async def test_answers_invalid_input_for_a_request_whose_values_cannot_be_read(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    method: str,
    url: str,
    body: dict[str, object] | None,
    field: str,
    code: str,
):
    response = await client.request(method, url, json=body, headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()["code"] == "invalid_input"
    assert response.json()["fields"] == [{"field": field, "issues": [{"code": code}]}]
    assert use_cases.current_users == []


async def test_answers_malformed_body_for_a_body_that_is_not_json(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    response = await client.post(
        "/v1/shorturls",
        content=b"{not json",
        headers={**AUTHORIZATION, "Content-Type": "application/json"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["code"] == "malformed_body"
    assert use_cases.current_users == []


async def test_answers_unavailable_when_the_use_case_raises_unavailable_error(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(GetShortURL).execute.side_effect = UnavailableError()

    response = await client.get(f"/v1/shorturls/{ID}", headers=AUTHORIZATION)

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json()["code"] == "unavailable"


async def test_logs_the_unavailable_error_with_what_failed(
    client: httpx.AsyncClient,
    use_cases: UseCaseDoubles,
    caplog: pytest.LogCaptureFixture,
):
    cause = ConnectionRefusedError()
    error = UnavailableError()
    error.__cause__ = cause
    use_cases.double(GetShortURL).execute.side_effect = error

    with caplog.at_level(logging.WARNING, logger="shortener.api.errors"):
        await client.get(f"/v1/shorturls/{ID}", headers=AUTHORIZATION)

    [record] = caplog.records
    assert record.exc_info is not None
    assert record.exc_info[1] is error
    assert record.exc_info[1].__cause__ is cause


async def test_answers_internal_error_when_the_use_case_raises_any_other_exception(
    client: httpx.AsyncClient, use_cases: UseCaseDoubles
):
    use_cases.double(CreateShortURL).execute.side_effect = RuntimeError()

    response = await client.post(
        "/v1/shorturls",
        json={"target_url": "https://example.com"},
        headers=AUTHORIZATION,
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["code"] == "internal_error"
