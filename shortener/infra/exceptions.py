from shortener.domain.shared.language import Language


class MissingEnvironmentVariableError(Exception):
    def __init__(self, var_names: list[str]):
        self.var_names = var_names
        super().__init__(f"Missing required environment variables: {var_names}")


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
