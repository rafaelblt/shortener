from dataclasses import dataclass
from http import HTTPStatus

from shortener.api.responses import JSONContent, NoContent, Redirect


@dataclass(frozen=True)
class Value:
    name: str


@dataclass(frozen=True)
class Encoded:
    text: str


def encode(value: Value) -> Encoded:
    return Encoded(text=value.name.upper())


def test_json_content_answers_the_value_of_ok_as_it_is():
    content = JSONContent()

    assert content.respond(Value("name")) == Value("name")
    assert content.model(Value) is Value


def test_json_content_with_encode_answers_what_encode_returns():
    content = JSONContent(encode=encode)

    assert content.respond(Value("name")) == Encoded("NAME")
    assert content.model(Value) is Encoded


def test_no_content_answers_no_content():
    response = NoContent().respond(None)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.body == b""


def test_redirect_answers_a_redirect_to_the_location_of_the_value():
    response = Redirect(lambda value: f"https://example.com/{value.name}").respond(
        Value("page")
    )

    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert response.headers["Location"] == "https://example.com/page"
