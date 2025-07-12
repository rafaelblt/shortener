from pydantic import BaseModel

from shortener.domain.shared.language import Language
from shortener.domain.user import User

from shortener.adapters.api.v1.schemas.entities import PublicUserSchema

from shortener.infra.translations.i18n import get_translator


class SuccessRegisterResponse(BaseModel):
    message: str
    user: PublicUserSchema

    @staticmethod
    def with_domain_user(user: User, lang: Language):
        _ = get_translator(lang)
        message = _("User registered successfully. Please check your email to verify your account.")
        schema = PublicUserSchema.from_domain(user)
        return SuccessRegisterResponse(message=message, user=schema)
