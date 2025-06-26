import pytest

from shortener.domain.shared.language import Language

from shortener.infra.translations.i18n import get_translator
from shortener.infra.exceptions import NotSupportedLanguageError


def test_get_translator_en():
    translator = get_translator(Language.EN)
    text = "test text"
    assert text == translator(text)


def test_get_translator_ptbr():
    translator = get_translator(Language.PT_BR)
    text = "test text"
    assert text == translator(text)


def test_get_translator_raises_not_supported_error():
    with pytest.raises(NotSupportedLanguageError) as error:
        get_translator(Language.FR)
    assert error.value.lang == Language.FR
