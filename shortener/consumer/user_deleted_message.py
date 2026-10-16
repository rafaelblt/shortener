import json

from uuid import UUID


def parse_user_id(body: bytes) -> UUID | None:
    """
    The ID of the deleted user in the body of a message, or None when the body
    isn't the one of the event. See docs/consumer.md#the-event
    """
    try:
        content = json.loads(body)
    except ValueError:
        # json raises JSONDecodeError for a body that isn't JSON, and
        # UnicodeDecodeError for one that isn't text, both ValueErrors.
        return None
    if not isinstance(content, dict) or not isinstance(content.get("user_id"), str):
        return None
    try:
        return UUID(content["user_id"])
    except ValueError:
        return None
