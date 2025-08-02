from shortener.domain.shared.language import Language
from shortener.infra import exceptions


def test_unknown_environment_template():
    unknown_template = "test unknown template"
    available_templates = ["a", "b", "c"]

    error = exceptions.UnknownEnvironmentTemplateError(
        unknown_template=unknown_template,
        available_templates=available_templates
    )

    assert error.unknown_template == unknown_template
    assert error.available_templates == available_templates
    assert unknown_template in str(error)
    assert str(available_templates) in str(error)


def test_missing_environment_variable():
    missing_vars = ["a", "b", "c", "d"]

    error = exceptions.MissingEnvironmentVariableError(missing_vars=missing_vars)

    assert error.missing_vars == missing_vars
    assert str(missing_vars) in str(error)


def test_environment_variable_conversion():
    var = "TEST_VAR"
    detail = "The value is TEST_VAR"

    error = exceptions.EnvironmentVariableConversionError(var=var, detail=detail)

    assert error.var == var
    assert error.detail == detail
    assert var in str(error)
    assert detail in str(error)


def test_missing_supported_language_translation():
    lang = Language.FR

    error = exceptions.MissingSupportedLanguageTranslationError(lang=lang)

    assert error.lang == lang
    assert str(lang) in str(error)


def test_not_supported_language():
    lang = Language.FR

    error = exceptions.NotSupportedLanguageError(lang=lang)

    assert error.lang == lang
    assert str(lang) in str(error)
