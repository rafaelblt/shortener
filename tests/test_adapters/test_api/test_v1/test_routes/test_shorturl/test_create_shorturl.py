import pytest

from http import HTTPStatus
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from shortener.domain.shorturl import ShortURL


@pytest.fixture
def route(shorturl_route: str):
    return f"{shorturl_route}"


def test_status_code_unauthorized_without_authenticated_user(
    client: TestClient, route: str
):
    response = client.post(route, json={})
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_status_code_unprocessable_entity_without_json_data(
    normal_user_client: TestClient, route: str
):
    response = normal_user_client.post(route, json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_status_code_unprocessable_entity_without_original_url(
    route: str,
    poor_user_client: TestClient,
    normal_shorturl: ShortURL
):
    response = poor_user_client.post(
        route, json={"custom_slug": normal_shorturl.slug}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_status_code_created_with_only_original_url(
    route: str,
    poor_user_client: TestClient,
    normal_shorturl: ShortURL,
):
    response = poor_user_client.post(
        route,
        json={"original_url": normal_shorturl.original_url}
    )
    assert response.status_code == HTTPStatus.CREATED, response.json()


def test_status_code_created_with_original_url_and_custom_slug(
    route: str,
    poor_user_client: TestClient,
    normal_shorturl: ShortURL,
):
    response = poor_user_client.post(
        route,
        json={
            "original_url": normal_shorturl.original_url,
            "custom_slug": normal_shorturl.slug
        }
    )
    assert response.status_code == HTTPStatus.CREATED


def test_json_response_data(
    route: str,
    poor_user_client: TestClient,
    normal_shorturl: ShortURL,
):
    response = poor_user_client.post(
        route,
        json={
            "original_url": normal_shorturl.original_url,
            "custom_slug": normal_shorturl.slug
        }
    )
    json = response.json()
    assert "shorturl" in json
    shorturl_json = json["shorturl"]

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    assert shorturl_json["id"] == 1
    assert shorturl_json["slug"] == normal_shorturl.slug
    assert shorturl_json["original_url"] == normal_shorturl.original_url
    assert shorturl_json["created_at"].startswith(today)
