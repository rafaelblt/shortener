from http import HTTPStatus
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from shortener.domain.shorturl.rules.slug_length import DEFAULT_RANDOM_SLUG_LENGTH


def test_without_json_data(client: TestClient, route: str):
    response = client.post(route, json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_with_only_original_url(client: TestClient, route: str):
    response = client.post(
        route, json={"original_url": "https://www.github.com"}
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["Location"] == route + "1" # .../shorturls/1

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    json = response.json()
    assert json["id"] == 1
    assert len(json["slug"]) == DEFAULT_RANDOM_SLUG_LENGTH
    assert json["original_url"] == "https://www.github.com"
    assert json["owner_id"] == None
    assert json["is_active"] == True
    assert json["visit_count"] == 0
    assert json["created_at"].startswith(today)
    assert json["expires_at"] == None
    assert json["last_accessed_at"] == None


def test_with_only_custom_slug(client: TestClient, route: str):
    response = client.post(route, json={"custom_slug": "git"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_with_original_url_and_custom_slug(client: TestClient, route: str):
    response = client.post(
        route,
        json={
            "original_url": "https://www.github.com",
            "custom_slug": "git"
        }
    )

    assert response.status_code == HTTPStatus.CREATED

    json = response.json()
    assert json["id"] == 1
    assert json["slug"] == "git"
    assert json["original_url"] == "https://www.github.com"


def test_with_original_url_and_owner_id(client: TestClient, route: str):
    response = client.post(
        route,
        json={
            "original_url": "https://www.github.com",
            "owner_id": 1
        }
    )

    assert response.status_code == HTTPStatus.CREATED

    json = response.json()
    assert json["id"] == 1
    assert json["original_url"] == "https://www.github.com"
    assert json["owner_id"] == None # TODO: assert json["owner_id"] == 1


def test_with_original_url_and_expirest_at(client: TestClient, route: str):
    expires_at = datetime.now(tz=timezone.utc)

    response = client.post(
        route,
        json={
            "original_url": "https://www.github.com",
            "expires_at": expires_at.timestamp()
        }
    )

    assert response.status_code == HTTPStatus.CREATED

    json = response.json()
    assert json["id"] == 1
    assert json["original_url"] == "https://www.github.com"
    assert json["expires_at"].startswith(expires_at.strftime("%Y-%m-%d"))
