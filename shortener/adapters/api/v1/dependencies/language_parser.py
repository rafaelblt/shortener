from typing import Optional, Annotated

from fastapi import Header, Depends

from shortener.domain.shared.language import Language
from shortener.infra.settings import settings


class LanguageParser:
    def __call__(self, accept_language: Optional[str] = Header(None)) -> Language:
        if accept_language:
            lang = self._get_first_lang(accept_language)
            if lang and lang in settings.supported_languages:
                return lang
        return Language.default()

    def _get_first_lang(self, accept_language: str) -> Optional[Language]:
        langs = accept_language.split(",")
        first_lang = langs[0].strip().split(";")[0]
        try:
            return Language(first_lang)
        except:
            return None


LanguageParserDependency = Annotated[Language, Depends(LanguageParser())]
