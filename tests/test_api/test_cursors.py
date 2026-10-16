import base64

from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import UUID

import pytest

from shortener.api.cursors import decode_cursor, encode_cursor
from shortener.use_cases.shorturl_cursor import ShortURLCursor


CURSOR = ShortURLCursor(
    created_at=datetime(
        2026, 1, 1, 12, 30, 15, 123456, tzinfo=timezone(timedelta(hours=-3))
    ),
    id=UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20"),
)


def encoded(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode()


def test_decode_cursor_returns_the_cursor_that_was_encoded():
    assert decode_cursor(encode_cursor(CURSOR)) == CURSOR


def test_encode_cursor_returns_text_a_url_carries_as_it_is():
    text = encode_cursor(CURSOR)
    assert quote(text, safe="") == text


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty"),
        pytest.param("not a cursor!", id="not base64"),
        pytest.param("é", id="not ascii"),
        pytest.param(encoded("2026-01-01T00:00:00+00:00"), id="without the id"),
        pytest.param(
            encoded("2026-01-01T00:00:00+00:00,not-a-uuid"), id="id that isn't a UUID"
        ),
        pytest.param(
            encoded(f"not-a-datetime,{CURSOR.id}"), id="created_at not a datetime"
        ),
        pytest.param(
            encoded(f"2026-01-01T00:00:00,{CURSOR.id}"), id="naive created_at"
        ),
        pytest.param(
            encoded(f"2026-01-01T00:00:00+00:00,{CURSOR.id},more"), id="more parts"
        ),
    ],
)
def test_decode_cursor_returns_none_for_text_that_encode_cursor_does_not_return(
    text: str,
):
    assert decode_cursor(text) is None
