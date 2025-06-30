from shortener.domain.shared.language import Language
from shortener.domain.services.email_template import EmailTemplate, RenderResult

from shortener.infra.settings import settings
from shortener.infra.templates.jinja import JinjaEnvironment
from shortener.infra.translations.i18n import get_translator


APP_NAME = settings.APP_NAME


class VerificationEmailTemplate(EmailTemplate):
    REQUIRED_CONTEXT_VARS = ["token", "user_name", "expires_minutes"]
    PLAIN_TEMPLATE_PATH = f"auth/verification_email.txt"

    def __init__(self, jinja_env: JinjaEnvironment):
        self._jinja_env = jinja_env

    def render(self, lang: Language, context: dict) -> RenderResult:
        _ = get_translator(lang)
        ctx = self.process_context(context)
        ctx["_"] = _

        subject = _("Verification Email - %(app_name)s") % {"app_name": APP_NAME}
        plain_template = self._jinja_env.get_template(self.PLAIN_TEMPLATE_PATH)
        
        return RenderResult(
            subject=subject,
            plain_body=plain_template.render(ctx),
            html_body=None
        )
    
    def process_context(self, context: dict) -> dict:
        self._validate_context(context)
        ctx = context.copy()
        token = ctx.pop("token")
        link = self.get_verification_link(token)
        ctx["verification_link"] = link
        return ctx

    def get_verification_link(self, token: str):
        return f"{settings.API_BASE_URL}/auth/verify-email?token={token}"
