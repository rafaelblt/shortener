from http import HTTPStatus

from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.schemas import MessageResponse
from shortener.adapters.api.v1.dependencies import VerifyEmailUseCaseDependency, LanguageParserDependency
from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.services.exceptions import AuthTokenExpiredError, AuthTokenInvalidError
from shortener.domain.user.exceptions import UserNotFoundError, UserStatusInvalidToVerifyEmailError

from shortener.infra.translations.i18n import get_translator

from . import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="User verified.",
    model=MessageResponse
)
responses.set_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Invalid email verification token.",
    model=ErrorResponse
)
responses.set_response(
    status_code=HTTPStatus.GONE,
    description="Email verification token has expired.",
    model=ErrorResponse
)
responses.set_response(
    status_code=HTTPStatus.CONFLICT,
    description="The user does not have pending email verification.",
    model=ErrorResponse
)


@router.get("/verify-email", responses=responses.get_responses())
async def verify_email(
    token: str,
    use_case: VerifyEmailUseCaseDependency,
    language: LanguageParserDependency
):
    error = {}
    _ = get_translator(language)
    try:
        await use_case.execute(token)
    except (AuthTokenInvalidError, UserNotFoundError):
        error["status_code"] = HTTPStatus.BAD_REQUEST
        error["error_code"] = "INVALID_EMAIL_VERIFICATION_TOKEN"
        error["detail"] = _("Invalid email verification token.")
    except AuthTokenExpiredError:
        error["status_code"] = HTTPStatus.GONE
        error["error_code"] = "EMAIL_VERIFICATION_TOKEN_EXPIRED"
        error["detail"] = _("Email verification token has expired.")
    except UserStatusInvalidToVerifyEmailError:
        error["status_code"] = HTTPStatus.CONFLICT
        error["error_code"] = ""
        error["detail"] = _("The user does not have pending email verification.")

    if error:
        return JSONResponse(
            status_code=error.pop("status_code"),
            content=error
        )

    return {"message": "Email successfully verified."}
