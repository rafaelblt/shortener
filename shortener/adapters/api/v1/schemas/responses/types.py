from http import HTTPStatus
from typing import Any


class FastAPIRouteResponses:
    def __init__(self):
        self._data = {}

    def set_response(
        self,
        status_code: HTTPStatus,
        description: str,
        model: Any,
    ):
        self._data[status_code] = {"description": description, "model": model}

    def get_responses(self) -> dict[int | str, dict[str, Any]]:
        return self._data
