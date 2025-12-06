from http import HTTPStatus
from typing import Any, TypedDict

from pydantic import BaseModel
from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse


class ResponseData(TypedDict):
    content: dict[str, Any]


class ResponseSchema(TypedDict):
    description: str
    model: Any
    content: dict


class StatusData(TypedDict):
    schema: ResponseSchema
    response: ResponseData


class FastAPIRouteResponses:
    def __init__(self):
        self._data: dict[HTTPStatus, StatusData] = {}

    def set_response(
        self,
        status_code: HTTPStatus,
        description: str,
        model: Any,
    ):
        self._data[status_code] = {
            "schema": {
                "description": description,
                "model": model,
                "content": {},
            },
            "response": {
                "content": {}
            }
        }

    def set_error_response(
        self,
        status_code: HTTPStatus,
        description: str,
        error_code: str,
    ):
        self._data[status_code] = {
            "schema": {
                "description": description,
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "code": error_code,
                            "detail": "The error detail"
                        }
                    }
                }
            },
            "response": {
                "content": {
                    "code": error_code, "detail": ""
                }
            }
        }

    def get_schema(self) -> dict[int | str, dict[str, Any]]:
        schema = {}
        for status_code, response in self._data.items():
            schema[status_code] = response["schema"]
        return schema

    def get_responses(self):
        return self.get_schema()
    
    def get_json_response_by_status_code(
        self, status_code: HTTPStatus, over_content: dict[str, Any] = {}
    ):
        content = self._data[status_code]["response"]["content"]
        content.update(over_content)
        return JSONResponse(
            status_code=status_code,
            content=content
        )


class RouteResponseSpec:
    def __init__(self):
        self._data = {}

    def add_json_response(
        self,
        status_code: HTTPStatus,
        description: str,
        model: BaseModel.__class__,
        examples: dict[str, dict],
    ):
        self._data[status_code] = {
            "description": description,
            "model": model,
            "examples": examples,
        }

    def get_schema(self):
        schema = {}
        for status_code, data in self._data.items():
            schema[status_code] = {
                "description": data["description"],
                "model": data["model"],
                "content": {
                    "application/json": {
                        "examples": data["examples"]
                    }
                }
            }
        return schema
    
    def get_example(
        self,
        status_code: HTTPStatus,
        title: str,
    ):
        return self._data[status_code]["examples"][title]
