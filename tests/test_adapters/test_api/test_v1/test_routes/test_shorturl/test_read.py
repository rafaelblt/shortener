import pytest

from http import HTTPStatus
from fastapi.testclient import TestClient

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.responses.shorturl.success_read import ShortURLReadSuccessResponse

from shortener.domain.shorturl.shorturl import ShortURL


@pytest.fixture
def route(shorturl_route: str):
    return f"{shorturl_route}"


def test_status_code_unauthorized_without_authenticated_user(
    client: TestClient, route: str
):
    response = client.get(f"{route}/1")
    assert response.status_code == HTTPStatus.UNAUTHORIZED, response.json()


def test_status_code_not_found_with_shorturl_non_existent(
    normal_user_client: TestClient, route: str
):
    response = normal_user_client.get(f"{route}/1000/")
    assert response.status_code == HTTPStatus.NOT_FOUND, response.json()


def test_json_response_with_shorturl_non_existent(
    normal_user_client: TestClient, route: str
):
    response = normal_user_client.get(f"{route}/1485714/")
    json = response.json()

    assert "code" in json
    assert "detail" in json
    assert json["code"] == ApiErrorCode.ITEM_NOT_FOUND


def test_status_code_ok(
    route: str,
    normal_user_client: TestClient,
    persistent_normal_shorturl: ShortURL,
):
    response = normal_user_client.get(
        f"{route}/{persistent_normal_shorturl.pk.raw_value}/"
    )
    assert response.status_code == HTTPStatus.OK, response.json()


def test_json_response(
    route: str,
    normal_user_client: TestClient,
    persistent_normal_shorturl: ShortURL,
):
    json = normal_user_client.get(
        f"{route}/{persistent_normal_shorturl.pk.raw_value}/"
    ).json()

    assert json == ShortURLReadSuccessResponse.with_shorturl(
        persistent_normal_shorturl
    ).model_dump(mode="json")
