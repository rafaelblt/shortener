import os
import gettext

from shortener.domain.shared.language import Language
from shortener.infra.settings import settings

from shortener.infra.exceptions import (
    NotSupportedLanguageError,
    MissingSupportedLanguageTranslationError
)


def default_translator(message: str) -> str:
    return message


def get_translator(lang: Language):
    if lang not in settings.supported_languages:
        raise NotSupportedLanguageError(lang=lang)
    
    if lang == Language.EN:
        return default_translator
    
    try:
        locales_dir = os.path.dirname(__file__)
        translation = gettext.translation(
            domain="messages",
            localedir=locales_dir,
            languages=[lang]
        )
        return translation.gettext
    except FileNotFoundError:
        raise MissingSupportedLanguageTranslationError(lang)
