from http import HTTPStatus


def test_create_shorturl(client):
    response = client.post(
        "/shorturls/",
        json={
            "original_url": "https://www.example.com",
            "custom_slug": "example",
        }
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["Location"] == "/shorturls/1"

    json = response.json()

    assert json["id"] == 1
    assert json["slug"] == "example"
    assert json["original_url"] == "https://www.example.com"
