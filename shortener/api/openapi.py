from collections.abc import Mapping
from typing import Any


def documented_headers(descriptions: Mapping[str, str]) -> dict[str, Any]:
    """
    The headers of a response, for the OpenAPI schema, from the description
    of each one. It is empty for no headers, since FastAPI would document an
    empty set of them.
    """
    if not descriptions:
        return {}
    return {
        "headers": {
            name: {"description": description, "schema": {"type": "string"}}
            for name, description in descriptions.items()
        }
    }
