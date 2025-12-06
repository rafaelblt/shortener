from http import HTTPStatus
from typing import TypedDict

from pydantic import BaseModel
from shortener.adapters.api.v1.schemas.responses.types import RouteResponseSpec


class ExampleSchema(BaseModel): ...


class ExampleSchemaWithAttrs(BaseModel):
    text: str
    number: int


class TestHelper:
    status_code = HTTPStatus.EARLY_HINTS
    description = "Description example"
    model = ExampleSchema
    examples = {"default": ExampleSchema().model_dump()}


def test_class_init():
    RouteResponseSpec()


def test_method_add_json_response():
    responses = RouteResponseSpec()
    helper = TestHelper()

    retrieved = responses.add_json_response(
        status_code=helper.status_code,
        description=helper.description,
        model=helper.model,
        examples=helper.examples
    )

    assert retrieved is None


def test_method_get_schema():
    responses = RouteResponseSpec()
    helper = TestHelper()
    responses.add_json_response(
        status_code=helper.status_code,
        description=helper.description,
        model=helper.model,
        examples=helper.examples
    )
    
    retrieved = responses.get_schema()

    assert retrieved == {
        helper.status_code: {
            "description": helper.description,
            "model": helper.model,
            "content": {
                "application/json": {
                    "examples": helper.examples
                }
            }
        }
    }


def test_method_get_example():
    examples = {
        "default": ExampleSchemaWithAttrs(
            text="asiufghuisdaf", number=5
        ).model_dump(),
        "another": ExampleSchemaWithAttrs(
            text="another example", number=10
        ).model_dump(),
        "scout": ExampleSchemaWithAttrs(
            text="scout example", number=404
        ).model_dump()
    }

    responses = RouteResponseSpec()
    helper = TestHelper()
    responses.add_json_response(
        status_code=helper.status_code,
        description=helper.description,
        model=helper.model,
        examples=examples
    )

    retrieved = responses.get_example(helper.status_code, title="default")
    assert retrieved == examples["default"]
