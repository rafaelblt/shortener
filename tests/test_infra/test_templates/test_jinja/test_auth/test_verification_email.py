import pytest

from shortener.domain.shared.language import Language
from shortener.domain.services.exceptions import MissingTemplateVariableError

from shortener.infra.settings import settings
from shortener.infra.translations.i18n import get_translator
from shortener.infra.templates.jinja.environment import JinjaEnvironment
from shortener.infra.templates.jinja.auth.verification_email import VerificationEmailTemplate


@pytest.fixture
def template():
    jinja_env = JinjaEnvironment()
    return VerificationEmailTemplate(jinja_env)


@pytest.fixture
def required_context():
    return {
        "token": "SUPERSECRETAUTHTOKEN",
        "user_name": "Peter Parker",
        "expires_minutes": "30"
    }


def test_attr_required_context_vars(
    template: VerificationEmailTemplate, required_context: dict
):
    assert template.REQUIRED_CONTEXT_VARS == list(required_context.keys())


def test_attr_plain_template_path(template: VerificationEmailTemplate):
    assert template.PLAIN_TEMPLATE_PATH == f"auth/verification_email.txt"


def test_template_in_jinja_env(template: VerificationEmailTemplate):
    jinja_env = JinjaEnvironment()
    assert jinja_env._env.loader
    templates = jinja_env._env.loader.list_templates()
    assert template.PLAIN_TEMPLATE_PATH in templates


def test_method_get_verification_link(template: VerificationEmailTemplate):
    token = "token"
    retrieved = template.get_verification_link(token)
    expected = f"{settings.API_BASE_URL}/auth/verify-email?token={token}"
    assert retrieved == expected


def test_method_process_context(
    template: VerificationEmailTemplate, required_context: dict
):
    token = required_context["token"]
    retrieved = template.process_context(required_context)
    assert "verification_link" in retrieved
    assert "token" not in retrieved
    assert retrieved["verification_link"] == template.get_verification_link(token)


def test_method_process_context_call_validate_context(
    template: VerificationEmailTemplate
):
    context = {}
    with pytest.raises(MissingTemplateVariableError) as error:
        template.process_context(context)
    assert error.value.var_names == template.REQUIRED_CONTEXT_VARS


def test_method_process_context_preserves_original_dict(
    template: VerificationEmailTemplate, required_context: dict   
):
    original_ctx = required_context.copy()
    template.process_context(required_context)
    assert required_context == original_ctx


def test_method_render(
    template: VerificationEmailTemplate, required_context: dict
):
    result = template.render(lang=Language.EN, context=required_context)
    subject = result["subject"]
    plain_body = result["plain_body"]
    html_body = result["html_body"]

    assert subject == f"Verification Email - {settings.APP_NAME}"
    assert html_body is None

    jinja_env = JinjaEnvironment()._env
    path = template.PLAIN_TEMPLATE_PATH
    token = required_context["token"]
    required_context["verification_link"] = template.get_verification_link(token)
    required_context["_"] = get_translator(Language.EN)
    expected_plain_body = jinja_env.get_template(path).render(required_context)

    assert plain_body == expected_plain_body


def test_method_render_with_language_ptbr(
    template: VerificationEmailTemplate, required_context: dict
):
    result = template.render(lang=Language.PT_BR, context=required_context)
    subject = result["subject"]
    plain_body = result["plain_body"]
    html_body = result["html_body"]

    assert subject == f"Verificação de Email - {settings.APP_NAME}"
    assert html_body is None

    jinja_env = JinjaEnvironment()._env
    path = template.PLAIN_TEMPLATE_PATH
    token = required_context["token"]
    required_context["verification_link"] = template.get_verification_link(token)
    required_context["_"] = get_translator(Language.PT_BR)
    expected_plain_body = jinja_env.get_template(path).render(required_context)

    assert plain_body == expected_plain_body
