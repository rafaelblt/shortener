import pytest

from datetime import datetime, timezone
from uuid import UUID

from shortener.api.cursors import decode_cursor
from shortener.api.shorturl_page_content import ShortURLPageContent
from shortener.domain import ShortURL
from shortener.use_cases.shorturl_cursor import ShortURLCursor
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_page import ShortURLPage


CURSOR = ShortURLCursor(
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    id=UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20"),
)


@pytest.fixture
def items(normal_shorturl: ShortURL) -> tuple[ShortURLDetails, ...]:
    return (ShortURLDetails.from_entity(normal_shorturl),)


def test_from_page_keeps_the_items_and_encodes_the_next_cursor(
    items: tuple[ShortURLDetails, ...],
):
    content = ShortURLPageContent.from_page(ShortURLPage(items, next_cursor=CURSOR))

    assert content.items == items
    assert content.next_cursor is not None
    assert decode_cursor(content.next_cursor) == CURSOR


def test_from_page_has_no_next_cursor_when_the_page_has_none(
    items: tuple[ShortURLDetails, ...],
):
    content = ShortURLPageContent.from_page(ShortURLPage(items, next_cursor=None))
    assert content.next_cursor is None
