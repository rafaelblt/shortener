import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient

from shortener.domain.shorturl import ShortURL
from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


@pytest.mark.asyncio
async def test_status_code_with_existent_id(
    client: TestClient,
    route: str,
    sqlalchemy_shorturl_repository: SQLAlchemyShortURLRepository,
    normal_shorturl: ShortURL
):
    shorturl = await sqlalchemy_shorturl_repository.save(normal_shorturl)
    response = client.delete(f"{route}/{shorturl.id}/")
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_if_shorturl_is_deleted(
    client: TestClient,
    route: str,
    sqlalchemy_shorturl_repository: SQLAlchemyShortURLRepository,
    normal_shorturl: ShortURL
):
    shorturl = await sqlalchemy_shorturl_repository.save(normal_shorturl)
    client.delete(f"{route}/{shorturl.id}/")
    exists = await sqlalchemy_shorturl_repository.exists_by_slug(normal_shorturl.slug)
    assert exists is False


@pytest.mark.asyncio
async def test_with_non_existent_id(
    client: TestClient,
    route: str,
):
    non_existent_id = 1
    response = client.delete(f"{route}/{non_existent_id}/")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "message":f"ShortURL with id {non_existent_id} not found for deletion."
    }
