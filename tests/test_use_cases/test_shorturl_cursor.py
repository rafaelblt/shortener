from dataclasses import FrozenInstanceError

import pytest

from shortener.domain import ShortURL
from shortener.use_cases.shorturl_cursor import ShortURLCursor


def test_from_entity_keeps_the_creation_moment_and_the_id_of_the_shorturl(
    normal_shorturl: ShortURL,
):
    assert ShortURLCursor.from_entity(normal_shorturl) == ShortURLCursor(
        created_at=normal_shorturl.created_at, id=normal_shorturl.id.value
    )


def test_is_immutable(normal_shorturl: ShortURL, old_shorturl: ShortURL):
    cursor = ShortURLCursor.from_entity(normal_shorturl)
    with pytest.raises(FrozenInstanceError):
        cursor.created_at = old_shorturl.created_at  # type: ignore
