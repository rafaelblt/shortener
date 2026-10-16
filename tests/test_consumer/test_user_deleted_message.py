import pytest

from uuid import UUID

from shortener.consumer.user_deleted_message import parse_user_id


USER_ID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")


def test_parse_user_id_returns_the_uuid_of_user_id():
    body = b'{"user_id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"}'
    assert parse_user_id(body) == USER_ID


def test_parse_user_id_ignores_the_other_fields():
    body = b'{"user_id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10", "deleted_at": 1}'
    assert parse_user_id(body) == USER_ID


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b"user_id", id="not JSON"),
        pytest.param(b"\xff\xfe\xfa", id="not text"),
        pytest.param(b'["0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"]', id="not an object"),
        pytest.param(b'{"id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"}', id="no user_id"),
        pytest.param(b'{"user_id": 1}', id="user_id not a string"),
        pytest.param(b'{"user_id": null}', id="user_id null"),
        pytest.param(b'{"user_id": "not-a-uuid"}', id="user_id not a UUID"),
    ],
)
def test_parse_user_id_returns_none_for_a_body_that_is_not_the_event(body: bytes):
    assert parse_user_id(body) is None
