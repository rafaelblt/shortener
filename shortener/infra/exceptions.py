from shortener.domain.shared.language import Language


class SettingsLoadError(Exception): ...


class UnknownEnvironmentTemplateError(SettingsLoadError):
    def __init__(self, unknown_template: str, available_templates: list[str]):
        self.unknown_template = unknown_template
        self.available_templates = available_templates
        super().__init__(
            (f"The environment template {unknown_template} does not exist. "
             f"The available templates are: {available_templates}")
        )


class MissingEnvironmentVariableError(SettingsLoadError):
    def __init__(self, missing_vars: list[str]):
        self.missing_vars = missing_vars
        super().__init__(f"Missing required environment variables: {missing_vars}")


class EnvironmentVariableConversionError(SettingsLoadError):
    def __init__(self, var: str, detail: str):
        self.var = var
        self.detail = detail
        super().__init__(("Failure when attempting to convert the environment "
                         f"variable '{var}': {detail}"))


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
