from http import HTTPStatus

from pydantic import BaseModel

from fastapi.responses import JSONResponse

from shortener.domain.shared.language import Language
from shortener.adapters.api.v1.schemas.responses import ErrorResponse
from shortener.infra.translations.i18n import get_translator


class FailLoginResponse(BaseModel):
    code: str = "INVALID_CREDENTIALS" 
    detail: str

    @classmethod
    def json_response(cls, lang: Language):
        _ = get_translator(lang)

        detail = _("Invalid email or password.")
        response = ErrorResponse(code=cls.code, detail=detail)

        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content=response
        )
