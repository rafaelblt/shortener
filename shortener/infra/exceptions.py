from shortener.domain.shared.language import Language


class MissingEnvironmentVariableError(Exception):
    def __init__(self, var_name: str):
        self.var_name = var_name
        super().__init__(f"Missing required environment variable: {var_name}")


class MissingSupportedLanguageTranslationError(Exception):
    def __init__(self, lang: Language):
        self.lang = lang
        super().__init__(
            f"The language '{lang}' is supported, but dont have translation file."
        )


class NotSupportedLanguageError(Exception):
    def __init__(self, lang: Language):
        self.lang = lang
        super().__init__(f"The language {lang} is not supported for translation.")
