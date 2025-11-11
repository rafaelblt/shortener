# import pytest

# from http import HTTPStatus
# from datetime import datetime, timezone
# from fastapi.testclient import TestClient

# from shortener.domain.shorturl import ShortURL
# from shortener.infra.db.repositories import SQLAlchemyShortURLRepository


# @pytest.mark.asyncio
# async def test_with_existent_id(
#     client: TestClient, 
#     sqlalchemy_shorturl_repository: SQLAlchemyShortURLRepository,
#     normal_shorturl: ShortURL
# ):
#     await sqlalchemy_shorturl_repository.save(normal_shorturl)

#     response = client.get("/api/v1/shorturls/1")
    
#     assert response.status_code == HTTPStatus.OK

#     today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
#     json = response.json()
#     assert json["id"] == 1
#     assert json["slug"] == normal_shorturl.slug
#     assert json["original_url"] == normal_shorturl.original_url
#     assert json["owner_id"] == normal_shorturl.owner_id
#     assert json["is_active"] == normal_shorturl.is_active
#     assert json["visit_count"] == normal_shorturl.visit_count
#     assert json["created_at"].startswith(today)
#     assert json["expires_at"] == normal_shorturl.expires_at
#     assert json["last_accessed_at"] == normal_shorturl.last_accessed_at


# def test_with_non_existent_id(client: TestClient):
#     response = client.get("/api/v1/shorturls/1")

#     assert response.status_code == HTTPStatus.NOT_FOUND
    
#     json = response.json()
#     assert json["message"] == "ShortURL not found"
