import base64

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator
from pydantic_core import PydanticCustomError

from shortener.shared.validation import IssueCode
from shortener.use_cases.shorturl_cursor import ShortURLCursor


def encode_cursor(cursor: ShortURLCursor) -> str:
    """
    The cursor as the text a client sends back. It is meant to be opaque, so
    the encoding can change. See docs/api.md#cursors
    """
    text = f"{cursor.created_at.isoformat()},{cursor.id}"
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def decode_cursor(text: str) -> ShortURLCursor | None:
    """Returns None when the text isn't one that encode_cursor() returns."""
    try:
        padding = "=" * (-len(text) % 4)
        created_at, id = base64.urlsafe_b64decode(text + padding).decode().split(",")
        cursor = ShortURLCursor(created_at=datetime.fromisoformat(created_at), id=UUID(id))
    except ValueError:
        return None
    if cursor.created_at.utcoffset() is None:
        return None
    return cursor


def _parse_cursor(text: str) -> ShortURLCursor:
    cursor = decode_cursor(text)
    if cursor is None:
        raise PydanticCustomError(
            IssueCode.INVALID_FORMAT.value, "The cursor isn't one a page returned"
        )
    return cursor


# How a request carries a ShortURLCursor: the text of encode_cursor(), which
# FastAPI turns back into the cursor, or answers INVALID_FORMAT.
CursorParameter = Annotated[str, AfterValidator(_parse_cursor)]
