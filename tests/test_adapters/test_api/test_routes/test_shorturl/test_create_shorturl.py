import pytest

from http import HTTPStatus

from datetime import datetime, timezone

from shortener.domain.shorturl.rules.slug_length import DEFAULT_RANDOM_SLUG_LENGTH


def test_with_only_original_url(client):
    response = client.post(
        "/shorturls/",
        json={
            "original_url": "https://www.github.com",
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["Location"] == "/shorturls/1"

    now = datetime.now(tz=timezone.utc)

    json = response.json()
    assert json["id"] == 1
    assert len(json["slug"]) == DEFAULT_RANDOM_SLUG_LENGTH
    assert json["original_url"] == "https://www.github.com"
    assert json["owner_id"] == None
    assert json["is_active"] == True
    assert json["visit_count"] == 0
    assert json["created_at"].startswith(f"{now.year}-")
    assert json["expires_at"] == None
    assert json["last_accessed_at"] == None
