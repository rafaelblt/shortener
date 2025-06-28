import pytest

from fastapi.params import Depends

from tests.utils.type_helpers import get_annotated_args

from shortener.domain.shared.language import Language
from shortener.adapters.api.v1.dependencies.language_parser import (
    LanguageParser, LanguageParserDependency
)


@pytest.fixture
def parser():
    return LanguageParser()


@pytest.mark.parametrize(
    ["lang", "expected"],
    [
        ("en", Language.EN),
        ("pt_br", Language.PT_BR),
        ("en;q=0.9", Language.EN),
        ("pt_br;q=0.5,en;q=0.9", Language.PT_BR),
        ("  pt_br  ,en;q=0.8", Language.PT_BR),
        ("fr", Language.default()),
        ("abc;q=0.1", Language.default()),
        (";;;;", Language.default()),
        ("", Language.default()),
    ]
)
def test_language_parser_call(parser: LanguageParser, lang, expected):
    assert parser(lang) == expected


def test_dependency():
    args = get_annotated_args(LanguageParserDependency)
    assert args[0] == Language
    assert isinstance(args[1], Depends)
    assert isinstance(args[1].dependency, LanguageParser)
