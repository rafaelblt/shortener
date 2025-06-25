import pytest

from shortener.domain.services.email_template import EmailTemplate, RenderResult
from shortener.domain.services.exceptions import MissingTemplateVariableError
from shortener.domain.shared.language import Language


@pytest.fixture
def template():
    class ImplEmailTemplate(EmailTemplate):
        REQUIRED_CONTEXT_VARS = ["a", "b", "c"]

        def render(self, lang: Language, context: dict[str, str]) -> RenderResult:
            return RenderResult(
                subject="subject",
                plain_body="plain_body",
                html_body="<html>body</html>"
            )
        
    return ImplEmailTemplate()


def test_validate_context_with_only_required_vars(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval"
    }
    assert template._validate_context(valid_ctx) is None


def test_validate_context_with_more_vars(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval",
        "var1":"val1",
        "var2":"val2",
        "var3":"val3"
    }
    assert template._validate_context(valid_ctx) is None


def test_validate_context_raises_missing_required_var(template: EmailTemplate):
    invalid_ctx = {}
    with pytest.raises(MissingTemplateVariableError) as error:
        template._validate_context(invalid_ctx)
    assert error.value.var_names == template.REQUIRED_CONTEXT_VARS


def test_validate_context_preserves_original_context(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval"
    }
    valid_ctx_copy = valid_ctx.copy()
    template._validate_context(valid_ctx)
    assert valid_ctx == valid_ctx_copy
