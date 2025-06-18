import pytest

from shortener.domain.services.email_template import EmailTemplate
from shortener.domain.services.exceptions import MissingTemplateVariableError


@pytest.fixture
def template():
    class ImplEmailTemplate(EmailTemplate):
        REQUIRED_CONTEXT_VARS = ["a", "b", "c"]

        def render_subject(self, lang, context) -> str:
            return "subject"

        def render_plain_body(self, lang, context) -> str:
            return "plain_body"

        def render_html_body(self, lang, context) -> str | None:
            return "<html>body</html>"
        
    return ImplEmailTemplate()


def test_process_context_with_only_required_vars(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval"
    }
    context = template.process_context(valid_ctx)
    assert context == valid_ctx


def test_process_context_with_more_vars(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval",
        "var1":"val1",
        "var2":"val2",
        "var3":"val3"
    }
    context = template.process_context(valid_ctx)
    assert context == valid_ctx


def test_process_context_raises_missing_required_var(template: EmailTemplate):
    invalid_ctx = {}
    with pytest.raises(MissingTemplateVariableError) as error:
        template.process_context(invalid_ctx)
    assert error.value.var_names == template.REQUIRED_CONTEXT_VARS


def test_process_context_preserves_original_context(template: EmailTemplate):
    valid_ctx = {
        "a":"aval",
        "b":"bval",
        "c":"cval"
    }
    valid_ctx_copy = valid_ctx.copy()
    template.process_context(valid_ctx)
    assert valid_ctx == valid_ctx_copy
