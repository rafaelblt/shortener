from http import HTTPStatus
from typing import Any, Optional

from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse


class FastAPIRouteResponses:
    def __init__(self):
        self._data = {}

    def set_response(
        self,
        status_code: HTTPStatus,
        description: str,
        model: Any,
    ):
        self._data[status_code] = {
            "description": description,
            "model": model,
        }

    def set_error_response(
        self,
        status_code: HTTPStatus,
        description: str,
        example_code: Optional[str] = None,
        example_detail: Optional[str] = None
    ):
        example_code = example_code or "EXAMPLE_ERROR_CODE"
        example_detail = example_detail or "Example detail."
        self._data[status_code] = {
            "description": description,
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": example_code,
                        "detail": example_detail
                    }
                }
            }
        }

    def get_responses(self) -> dict[int | str, dict[str, Any]]:
        return self._data
