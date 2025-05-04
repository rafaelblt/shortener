import pytest

from http import HTTPStatus
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from shortener.domain.shorturl.fields.slug import DEFAULT_RANDOM_SLUG_LENGTH


def test_status_code_unprocessable_entity_without_json_data(
    client: TestClient, route: str
):
    response = client.post(route, json={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "json",
    [
        {"custom_slug": "short"},
        {"owner_id": 1},
        {"custom_slug": "tests", "owner_id": 1},
    ]
)
def test_status_code_unprocessable_entity_without_original_url(
    client: TestClient, route: str, json: dict
):
    response = client.post(route, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "json",
    [
        {"custom_slug": "short"},
        {"original_url": "https://google.com"},
        {"custom_slug": "tests", "original_url": "https://youtube.com"},
    ]
)
def test_status_code_unprocessable_entity_without_owner_id(
    client: TestClient, route: str, json: dict
):
    response = client.post(route, json=json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# TODO: review tests when user route tests are working
# def test_response_header_location(client: TestClient, route: str):
#     response = client.post(
#         route, json={"original_url": "https://www.github.com"}
#     )
#     assert response.headers["Location"] == route + "/1" # .../shorturls/1


# def test_json_data(client: TestClient, route: str):
#     response = client.post(
#         route, json={"original_url": "https://www.github.com"}
#     )
#     today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
#     json = response.json()
#     assert json["id"] == 1
#     assert len(json["slug"]) == DEFAULT_RANDOM_SLUG_LENGTH
#     assert json["original_url"] == "https://www.github.com"
#     assert json["owner_id"] == None
#     assert json["is_active"] == True
#     assert json["visit_count"] == 0
#     assert json["created_at"].startswith(today)
#     assert json["expires_at"] == None
#     assert json["last_accessed_at"] == None


# def test_status_code_created_with_original_url_and_custom_slug(
#     client: TestClient, route: str
# ):
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "custom_slug": "git"
#         }
#     )
#     assert response.status_code == HTTPStatus.CREATED


# def test_json_data_with_original_url_and_custom_slug(
#     client: TestClient, route: str
# ):
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "custom_slug": "git"
#         }
#     )
#     json = response.json()
#     assert json["id"] == 1
#     assert json["slug"] == "git"
#     assert json["original_url"] == "https://www.github.com"


# def test_status_code_created_with_original_url_and_owner_id(
#     client: TestClient, route: str
# ):
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "owner_id": 1
#         }
#     )
#     assert response.status_code == HTTPStatus.CREATED


# def test_json_data_with_original_url_and_owner_id(
#     client: TestClient, route: str
# ):
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "owner_id": 1
#         }
#     )
#     json = response.json()
#     assert json["id"] == 1
#     assert json["original_url"] == "https://www.github.com"
#     assert json["owner_id"] == None # TODO: assert json["owner_id"] == 1


# def test_status_code_created_with_original_url_and_expirest_at(
#     client: TestClient, route: str
# ):
#     expires_at = datetime.now(tz=timezone.utc)
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "expires_at": expires_at.timestamp()
#         }
#     )
#     assert response.status_code == HTTPStatus.CREATED


# def test_status_code_created_with_original_url_and_expirest_at(
#     client: TestClient, route: str
# ):
#     expires_at = datetime.now(tz=timezone.utc)
#     response = client.post(
#         route,
#         json={
#             "original_url": "https://www.github.com",
#             "expires_at": expires_at.timestamp()
#         }
#     )
#     json = response.json()
#     assert json["id"] == 1
#     assert json["original_url"] == "https://www.github.com"
#     assert json["expires_at"].startswith(expires_at.strftime("%Y-%m-%d"))
